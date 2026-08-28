"""Shared plumbing for the deterministic control layer (playbook §5.4).

Every gate: reads version-controlled policy, decides deterministically, and writes
a JSON result to evidence/. Evidence is a by-product of the control operating,
not a separate reconstruction exercise (§5.5, principle 5).

No model is ever consulted here. Principle 4: no model in the gate.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
from datetime import UTC, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"
CODEOWNERS = ROOT / "CODEOWNERS"


def load_yaml(relative: str) -> dict:
    import yaml

    return yaml.safe_load((ROOT / relative).read_text())


def _git(*args: str) -> list[str]:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return [line for line in result.stdout.split("\n") if line] if result.returncode == 0 else []


def changed_files(base: str | None = None) -> list[str]:
    """Files this change set touches.

    The union of two things, because either alone is wrong somewhere:
      * committed work, diffed against the merge base (what CI sees);
      * uncommitted work, staged and unstaged (what you have in front of you).

    A gate that only reads committed history passes on the edit you just made, which
    is the moment you most wanted it to speak up.
    """
    base = base or os.environ.get("GATE_BASE_REF") or "origin/main"
    committed: list[str] = []
    for rev in (base, "origin/HEAD", "main"):
        if _git("rev-parse", "--verify", "--quiet", rev):
            committed = _git("diff", "--name-only", f"{rev}...HEAD")
            break
    else:
        committed = _git("diff", "--name-only", "HEAD~1...HEAD")

    working = _git("diff", "--name-only", "HEAD") + _git("diff", "--name-only", "--cached")
    untracked = _git("ls-files", "--others", "--exclude-standard")
    return sorted(set(committed) | set(working) | set(untracked))


def report(control_id: str, name: str, passed: bool, findings: list[str], **detail) -> int:
    """Write the evidence record, print a human line, return an exit code."""
    EVIDENCE.mkdir(exist_ok=True)
    record = {
        "control_id": control_id,
        "gate": name,
        "result": "pass" if passed else "fail",
        "findings": findings,
        "timestamp": datetime.now(UTC).isoformat(),
        "commit": os.environ.get("GITHUB_SHA", _head()),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "actor": os.environ.get("GITHUB_ACTOR", os.environ.get("USER", "local")),
        **detail,
    }
    (EVIDENCE / f"{name}.json").write_text(json.dumps(record, indent=2) + "\n")

    mark = "PASS" if passed else "FAIL"
    print(f"[{mark}] {control_id} {name}")
    for finding in findings:
        print(f"       {finding}", file=sys.stderr if not passed else sys.stdout)
    return 0 if passed else 1


def _head() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return result.stdout.strip() or "unknown"


def matches(path: str, pattern: str) -> bool:
    """Glob match where `**` spans directory separators."""
    import fnmatch
    import re

    regex = re.escape(pattern).replace(r"\*\*/", "(?:.*/)?").replace(r"\*\*", ".*")
    regex = regex.replace(r"\*", "[^/]*").replace(r"\?", "[^/]")
    return re.fullmatch(regex, path) is not None or fnmatch.fnmatch(path, pattern)

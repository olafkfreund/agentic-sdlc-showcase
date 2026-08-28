#!/usr/bin/env python3
"""SOD-01 — CODEOWNERS must actually resolve.

GitHub **silently ignores** a CODEOWNERS rule whose owner does not exist, is not
publicly visible, or lacks write access. The rule stays in the file, the branch
protection still says "require review from Code Owners", and the requirement is
satisfied by nobody.

That is a control which reads as operating while it is not — the failure mode this
whole playbook is about. This gate calls GitHub's own CODEOWNERS validator and fails
the build on any unresolved owner.

Offline (no token), it falls back to checking the file parses and every path prefix
it names still exists, so a rule protecting a directory that was renamed away is
caught too.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import gate  # noqa: E402


def github_errors(repo: str) -> list[dict] | None:
    """GitHub's own validator. None when it cannot be reached.

    Validates the ref under review, not the default branch — otherwise a pull
    request that breaks CODEOWNERS passes and the breakage lands on main.
    """
    ref = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    url = f"repos/{repo}/codeowners/errors" + (f"?ref={ref}" if ref else "")
    out = subprocess.run(["gh", "api", url], capture_output=True, text=True)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout).get("errors", [])
    except json.JSONDecodeError:
        return None


def stale_paths() -> list[str]:
    """Rules guarding a path that no longer exists guard nothing."""
    findings = []
    for number, line in enumerate(gate.CODEOWNERS.read_text().splitlines(), 1):
        line = line.split("#")[0].strip()
        if not line:
            continue
        pattern = line.split()[0]
        if pattern == "*":
            continue
        target = pattern.strip("/").rstrip("*").rstrip("/")
        if target and not (gate.ROOT / target).exists():
            findings.append(f"line {number}: rule guards {pattern!r}, which does not exist")
    return findings


def unowned_controls() -> list[str]:
    """The control layer must have an owner. A catch-all `*` is not one."""
    text = gate.CODEOWNERS.read_text()
    must_be_named = ["/policy/", "/.github/workflows/", "/scripts/", "/intent/"]
    return [
        f"{path} has no explicit CODEOWNERS rule; the catch-all is not an accountability"
        for path in must_be_named
        if not re.search(rf"^{re.escape(path)}\s+\S", text, re.M)
    ]


def main() -> int:
    if not gate.CODEOWNERS.exists():
        return gate.report("SOD-01", "codeowners", False, ["no CODEOWNERS file"])

    findings = stale_paths() + unowned_controls()

    repo = os.environ.get("GITHUB_REPOSITORY")
    errors = github_errors(repo) if repo else None
    if errors is None:
        print("  (GitHub CODEOWNERS validator unavailable; checked the file only)")
    else:
        # One line per unresolved owner. GitHub's message embeds the offending
        # source line and a caret, which is unreadable in a CI log at 18 errors.
        seen: set[str] = set()
        for error in errors:
            first = error.get("message", "").split("\n")[0].rstrip(".")
            key = f"line {error.get('line')}: {first}"
            if key not in seen:
                seen.add(key)
                findings.append(key)

    return gate.report(
        "SOD-01",
        "codeowners",
        not findings,
        findings,
        validator="github" if errors is not None else "offline",
        unresolved_owners=len(errors) if errors is not None else None,
    )


if __name__ == "__main__":
    raise SystemExit(main())

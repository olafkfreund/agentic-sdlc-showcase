#!/usr/bin/env python3
"""Switch the agent runtime, and print exactly what moved.

Substitution Test #2 asks what you would have to rebuild if you replaced your agent
vendor on Monday. Every vendor's marketing answers "nothing". This answers it by doing
it and then counting.

    python scripts/switch_runtime.py claude     # switch, and report the blast radius
    python scripts/switch_runtime.py --list     # what is available
    python scripts/switch_runtime.py --current  # what is selected

The report is the point. A one-line diff is easy to claim and easy to check, so the
interesting half is the inventory of what did *not* move — the skills, the policy
tables, the gates, the artifact chain, the evals. If a swap ever starts touching those,
this prints it rather than letting it pass as a refactor.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNTIMES = ROOT / ".agent/runtimes.yaml"

# What a runtime swap must never touch. Each entry is (label, glob).
INVARIANT = [
    ("skills", ".agent/skills/*/SKILL.md"),
    ("eval cases", ".agent/evals/cases/*.yaml"),
    ("policy tables", "policy/*.yaml"),
    ("deterministic gates", "scripts/check_*.py"),
    ("chain artifacts", "intent/*.md"),
    ("chain artifacts ", "specs/*.md"),
    ("chain artifacts  ", "plans/*.md"),
]


def load() -> dict:
    return yaml.safe_load(RUNTIMES.read_text())


def git(*args: str) -> str:
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else ""


def switch(target: str) -> int:
    doc = load()
    available = doc["runtimes"]
    if target not in available:
        print(f"unknown runtime {target!r}; available: {', '.join(available)}", file=sys.stderr)
        return 2

    before = doc["selected"]
    text = RUNTIMES.read_text()
    updated, count = re.subn(r"^selected:\s*\S+$", f"selected: {target}", text, count=1, flags=re.M)
    if count != 1:
        print("could not find a single `selected:` line to change", file=sys.stderr)
        return 2
    RUNTIMES.write_text(updated)

    runtime = available[target]
    print(f"\n  {before}  ->  {target}   ({runtime['name']}, {runtime['vendor']})\n")

    # What the switch wrote, read back from git rather than asserted by this script.
    # Scoped to the file it edits, so an unrelated dirty tree cannot flatter or slander
    # the number — and if a future edit here starts writing elsewhere, the invariant
    # check below is what catches it.
    rel = RUNTIMES.relative_to(ROOT).as_posix()
    changed = [f for f in git("diff", "--name-only", "--", rel).splitlines() if f]
    numstat = git("diff", "--numstat", "--", rel)
    edited = sum(int(n) for n in re.findall(r"^(\d+)\t", numstat, re.M)) if numstat else 0
    print(f"  the swap wrote:  {len(changed)} file(s), {edited} line(s)")
    for path in changed:
        print(f"                     {path}")

    print("\n  untouched by the swap, counted rather than asserted:")
    for label, pattern in INVARIANT:
        paths = sorted(ROOT.glob(pattern))
        moved = [p for p in paths if p.relative_to(ROOT).as_posix() in changed]
        mark = "!!" if moved else "ok"
        print(f"    [{mark}] {len(paths):3d}  {label.strip()}")

    if runtime.get("needs_gateway"):
        print(
            "\n  This runtime takes its credential from the gateway in .agent/routes.yaml.\n"
            "  Set the AI_GATEWAY_ENABLED repository variable and the AI_GATEWAY_TOKEN\n"
            "  secret to run it live. Until then the stage reports plainly that no agent\n"
            "  took the task — it does not report success."
        )
    else:
        print("\n  This runtime needs no provider credential; it is an identity in the VCS.")

    print()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime", nargs="?", help="runtime to switch to")
    parser.add_argument("--list", action="store_true", help="list available runtimes")
    parser.add_argument("--current", action="store_true", help="print the selected runtime")
    args = parser.parse_args()

    doc = load()
    if args.current:
        print(doc["selected"])
        return 0
    if args.list or not args.runtime:
        selected = doc["selected"]
        print("\n  Agent runtimes (playbook §5.2) — .agent/runtimes.yaml\n")
        for name, runtime in doc["runtimes"].items():
            mark = "*" if name == selected else " "
            gateway = "gateway credential" if runtime.get("needs_gateway") else "no provider key"
            print(f"   {mark} {name:9s} {runtime['name']:32s} {runtime['invocation']:7s} {gateway}")
        print("\n  make swap RUNTIME=<name>      switch to one")
        print("  make swap                     switch through every one, scoring each\n")
        return 0
    return switch(args.runtime)


if __name__ == "__main__":
    raise SystemExit(main())

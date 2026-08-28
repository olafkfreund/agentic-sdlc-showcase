#!/usr/bin/env python3
"""Which merged intent has no spec yet? Stage 2 trigger.

Deterministic: the workflow decides what to ask the agent for, the agent does not
decide what to work on.
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import artifacts  # noqa: E402


def already_requested(change_id: str) -> bool:
    """Is there already an open issue asking for this spec?

    The trigger fires on every push to main touching intent/**, so without this it
    opens a fresh issue for the same change each time — and an automation that
    produces duplicates gets muted, which costs you the whole loop.
    """
    out = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--state",
            "open",
            "--label",
            "spec",
            "--search",
            change_id,
            "--json",
            "title",
        ],
        capture_output=True,
        text=True,
    )
    if out.returncode != 0:
        return False  # cannot tell; a duplicate beats a missed request
    try:
        return any(change_id in i.get("title", "") for i in json.loads(out.stdout))
    except json.JSONDecodeError:
        return False


def main() -> int:
    found = artifacts.all_artifacts()
    with_intent = {a.change_id for a in found if a.stage == "intent" and a.change_id}
    with_spec = {a.change_id for a in found if a.stage == "spec" and a.change_id}
    pending = sorted(with_intent - with_spec)

    change_id = os.environ.get("INPUT_CHANGE_ID") or (pending[0] if pending else "")
    duplicate = bool(change_id) and already_requested(change_id)

    print(f"pending: {pending or 'none'}")
    print(f"selected: {change_id or 'none'}")
    if duplicate:
        print(f"an open issue already requests the spec for {change_id}; not asking twice")

    if out := os.environ.get("GITHUB_OUTPUT"):
        with open(out, "a") as fh:
            fh.write(f"change_id={change_id}\npending={' '.join(pending)}\n")
            fh.write(f"already_requested={str(duplicate).lower()}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

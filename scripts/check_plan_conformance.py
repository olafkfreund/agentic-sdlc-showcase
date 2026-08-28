#!/usr/bin/env python3
"""TRC-01 — Traceability of decisions. Plan-to-diff conformance (Stage 3.4).

Nothing gets implemented without an accepted written plan, and where the
implementation departs from the plan, the plan is updated in the same change.
This gate makes that structural rather than a matter of discipline.

The plan's `## Files` section lists the paths it intends to touch. A code file in
the diff that no plan claims is a departure; the fix is to update the plan.
"""

import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import artifacts  # noqa: E402
import gate  # noqa: E402

# Paths that are chain bookkeeping rather than implementation, so need no plan entry.
EXEMPT = ("intent/", "specs/", "plans/", "docs/", "evidence/", "README.md", ".gitignore")


def main() -> int:
    files = [f for f in gate.changed_files() if not f.startswith(EXEMPT)]
    claimed = artifacts.claimed_paths()
    findings = [
        f"{path}: changed but claimed by no plan's `## Files` section — "
        f"add it to the plan for this change (Stage 3.4)"
        for path in files
        if not any(gate.matches(path, pattern) for pattern in claimed)
    ]

    conformance = 1.0 if not files else 1 - len(findings) / len(files)
    return gate.report(
        "TRC-01",
        "plan_conformance",
        not findings,
        findings,
        files_changed=len(files),
        conformance_rate=round(conformance, 3),
        plans=sorted(set(claimed.values())),
    )


if __name__ == "__main__":
    raise SystemExit(main())

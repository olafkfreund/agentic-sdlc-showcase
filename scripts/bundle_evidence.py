#!/usr/bin/env python3
"""Collect the gate evidence into one predicate for the release attestation.

The gate results travel with the artifact, so "which controls ran on the thing that is
in production" is answerable from the artifact alone rather than by correlating build
logs after the fact (§5.5, pipeline attestations).

DEMO DATA: this bundle is produced against a synthetic service.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import gate  # noqa: E402


def main() -> int:
    controls = {c["id"]: c for c in gate.load_yaml("policy/controls.yaml")["controls"]}
    records = []
    for path in sorted(gate.EVIDENCE.glob("*.json")):
        if path.name == "bundle.json":
            continue
        try:
            records.append(json.loads(path.read_text()))
        except json.JSONDecodeError:
            print(f"::warning::{path} is not valid JSON; excluded from the bundle")

    ran = {r["control_id"] for r in records}
    # A control that was supposed to run and did not is the finding that matters.
    # Silence here would read as coverage.
    not_run = sorted(set(controls) - ran)

    bundle = {
        "disclaimer": "DEMO DATA — synthetic service, not an institution's audit record.",
        "generated_at": datetime.now(UTC).isoformat(),
        "commit": os.environ.get("GITHUB_SHA", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "controls_declared": sorted(controls),
        "controls_evidenced": sorted(ran),
        "controls_without_evidence": not_run,
        "all_passed": all(r["result"] == "pass" for r in records),
        "results": records,
    }
    (gate.EVIDENCE / "bundle.json").write_text(json.dumps(bundle, indent=2) + "\n")

    print(f"bundled {len(records)} gate result(s) covering {len(ran)} control(s)")
    if not_run:
        print(f"::warning::no evidence for {not_run} — these controls did not run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

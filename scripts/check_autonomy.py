#!/usr/bin/env python3
"""HUM-14 — Human oversight, enforced by the published autonomy matrix (§8.3).

Two checks:
  1. The declared autonomy_tier does not exceed max_tier[risk_class][environment].
  2. The declared risk_class is not below the floor forced by the paths touched.
     Otherwise a material change self-declares as routine and walks past the gate.
"""

import os
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import artifacts  # noqa: E402
import gate  # noqa: E402

ENVIRONMENT = os.environ.get("TARGET_ENVIRONMENT", "development")


def main() -> int:
    matrix_doc = gate.load_yaml("policy/autonomy-matrix.yaml")
    risk_doc = gate.load_yaml("policy/risk-classes.yaml")
    order = matrix_doc["order"]
    matrix = matrix_doc["matrix"]
    floors = risk_doc.get("path_floors", [])

    files = gate.changed_files()
    findings: list[str] = []
    checked = 0

    # The floor is per plan, not per change set. A plan that claims no sensitive
    # path is not dragged to R3 because some other plan in the same push does.
    claimed = artifacts.claimed_paths()
    per_plan: dict[str, tuple[str, str]] = {}
    for path in files:
        # A path can be claimed by more than one plan (a broad `service/**` and a
        # specific `service/app/models.py`). The floor binds every plan that claims
        # it — picking one arbitrarily is how a material change slips through.
        owners = [plan for pattern, plan in claimed.items() if gate.matches(path, pattern)]
        if not owners:
            continue  # unclaimed paths are check_plan_conformance's finding, not ours
        for rule in floors:
            if not gate.matches(path, rule["pattern"]):
                continue
            for owner in owners:
                current, _ = per_plan.get(owner, ("R1", ""))
                if rule["min_class"] > current:
                    per_plan[owner] = (rule["min_class"], f"{path} ({rule['reason']})")

    for artifact in artifacts.all_artifacts():
        if artifact.errors or artifact.stage != "plan":
            continue
        checked += 1
        declared_risk = artifact.header["risk_class"]
        tier = artifact.header["autonomy_tier"]
        name = artifact.path.name

        floor, floor_reason = per_plan.get(name, ("R1", ""))
        if declared_risk < floor:
            findings.append(
                f"{name}: declares {declared_risk} but claims {floor_reason}, "
                f"which forces a floor of {floor} (policy/risk-classes.yaml)"
            )
            declared_risk = floor

        allowed = matrix[declared_risk][ENVIRONMENT]
        if order.index(tier) > order.index(allowed):
            findings.append(
                f"{name}: autonomy_tier {tier} exceeds {allowed}, the maximum for "
                f"{declared_risk} in {ENVIRONMENT} (policy/autonomy-matrix.yaml §8.3)"
            )

    return gate.report(
        "HUM-14",
        "autonomy",
        not findings,
        findings,
        environment=ENVIRONMENT,
        risk_floors={k: v[0] for k, v in per_plan.items()},
        plans_checked=checked,
    )


if __name__ == "__main__":
    raise SystemExit(main())

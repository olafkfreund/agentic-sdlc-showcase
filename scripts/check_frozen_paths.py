#!/usr/bin/env python3
"""FRZ-01 — Change confined to supported components (Stage 3 control point).

Frozen and generated paths are declared in policy/frozen-paths.yaml. An exception
is possible, but only at R3 with an architect approval, and it has to be declared
in the plan header — not argued for in a PR comment.
"""

import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import artifacts  # noqa: E402
import gate  # noqa: E402


def declared_exceptions() -> dict[str, str]:
    """Frozen-path exceptions claimed by plans, keyed by path."""
    out = {}
    for artifact in artifacts.all_artifacts():
        if artifact.stage != "plan":
            continue
        for path in artifact.header.get("frozen_path_exception", []) or []:
            out[path] = artifact.path.name
    return out


def main() -> int:
    policy = gate.load_yaml("policy/frozen-paths.yaml")
    requires = policy.get("exception_requires", {})
    exceptions = declared_exceptions()
    plans = {a.path.name: a for a in artifacts.all_artifacts() if a.stage == "plan"}

    findings = []
    for path in gate.changed_files():
        for rule in policy["frozen"]:
            if not gate.matches(path, rule["path"]):
                continue
            plan_name = exceptions.get(rule["path"]) or exceptions.get(path)
            if not plan_name:
                findings.append(
                    f"{path}: frozen — {rule['reason']} Owner {rule['owner']}. "
                    f"To change it, declare `frozen_path_exception` in the plan header."
                )
            elif plans[plan_name].header.get("risk_class") != requires.get("risk_class"):
                findings.append(
                    f"{path}: frozen-path exception in {plan_name} requires risk_class "
                    f"{requires['risk_class']} and {requires['approver_team']} approval"
                )

    return gate.report(
        "FRZ-01",
        "frozen_paths",
        not findings,
        findings,
        frozen_patterns=[r["path"] for r in policy["frozen"]],
        exceptions_declared=sorted(exceptions),
    )


if __name__ == "__main__":
    raise SystemExit(main())

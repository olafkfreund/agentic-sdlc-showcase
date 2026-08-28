#!/usr/bin/env python3
"""CHG-04 — Authorised change only.

Every artifact in the chain carries a valid §6.2 header, and every change_id that
has a plan also has the spec and intent it derives from. Without this the chain is
markdown; with it, the chain is queryable evidence.
"""

import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import artifacts  # noqa: E402
import gate  # noqa: E402


def main() -> int:
    found = artifacts.all_artifacts()
    findings = [f"{a.path.name}: {e}" for a in found for e in a.errors]

    # The chain must not have gaps: a plan implies a spec implies an intent.
    predecessor = {"plan": "spec", "spec": "intent"}
    for artifact in found:
        if artifact.errors or not artifact.change_id:
            continue
        need = predecessor.get(artifact.stage)
        if need and need not in artifacts.chain(artifact.change_id):
            findings.append(
                f"{artifact.path.name}: {artifact.stage} for {artifact.change_id} "
                f"has no {need} in the chain (§6.1)"
            )

    return gate.report(
        "CHG-04",
        "artifact_header",
        not findings,
        findings,
        artifacts_checked=len(found),
        change_ids=sorted({a.change_id for a in found if a.change_id}),
    )


if __name__ == "__main__":
    raise SystemExit(main())

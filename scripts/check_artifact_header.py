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

    # ...and it must not trail off. The rule above only looks backwards, so an intent that
    # never became a spec passed silently and forever. A chain that stops short of a plan
    # has to say so on its last artifact: `blocked` (waiting on a named decision, will
    # resume) or `dismissed` (triaged, will not).
    #
    # Stopping is legitimate and common — a policy conflict that second line must resolve, an
    # anomaly triaged as noise. What is not legitimate is stopping silently, because then a
    # deliberate halt and an abandoned change are indistinguishable to everyone downstream,
    # including the site that publishes them both as though work were in progress.
    stopped = 0
    for change_id in sorted({a.change_id for a in found if a.change_id}):
        chain = artifacts.chain(change_id)
        if "plan" in chain:
            continue
        last = chain.get("spec") or chain.get("intent")
        if last is None or last.errors:
            continue
        if last.header.get("status") in artifacts.STATUSES:
            stopped += 1
            continue
        findings.append(
            f"{last.path.name}: chain {change_id} stops at {last.stage} with no plan and "
            f"declares no status — set `status: blocked` or `status: dismissed` with a "
            f"`status_reason` (§6.1)"
        )

    return gate.report(
        "CHG-04",
        "artifact_header",
        not findings,
        findings,
        artifacts_checked=len(found),
        change_ids=sorted({a.change_id for a in found if a.change_id}),
        chains_deliberately_stopped=stopped,
    )


if __name__ == "__main__":
    raise SystemExit(main())

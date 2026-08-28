#!/usr/bin/env python3
"""Stage 6.4 — the agent writes its diagnosis as an intent.md in the Stage 1 format.

The anomaly, the evidence, a proposed outcome and open questions. From there it
flows through the normal stages, which is what makes the loop a loop rather than
an alerting system.

The *content* of a real diagnosis comes from the agent; this script produces the
artifact with a valid header and the detection evidence already in it, so the agent
is never the thing that has to get the header right.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import artifacts  # noqa: E402
import gate  # noqa: E402

TEMPLATE = """---
change_id: {change_id}
risk_class: R2
autonomy_tier: A2
controls: [CHG-04, TRC-01]
data_classification: internal
originator: svc-agent-platform@example.com
agent_identity: svc-agent-platform
model_route: gateway/tier-balanced
supersedes: null
incident_id: null
---

# Intent: {metric} anomaly at {sigma} sigma

> Raised by the deterministic detector in `scripts/detect_anomaly.py`. **No human was
> in the invocation path.** A human triages this: fix now, schedule, or dismiss.
> Dismissals tune the bands.

## Problem

`{metric}` reached **{latest}**, which is **{sigma} standard deviations** from its
30-day rolling baseline of {mean} (sd {stdev}).

Rules fired:

{rules}

## Suspect deploy

{suspect}

## Who is affected

Determined at triage. The metric is a service-level signal; the population behind it
is not known to the detector and the detector does not guess.

## Success criteria

1. `{metric}` returns to within one sigma of its baseline and stays there for 48 hours.
2. The cause is identified and either fixed or explicitly accepted with a named owner.
3. If this class of anomaly can recur, a permanent eval is added to `.agent/evals/cases/`
   by the team that owns it (Stage 4.6).

## Out of scope

Changing the detection bands to stop this firing. If the band is wrong, that is a
separate change to `ops/response-tiers.yaml` with its own record.

## Constraints

The agent holds no production write access. Any resulting change goes through the
normal PR gate at the autonomy the matrix permits.

## Open questions

- Is this a real regression or a change in traffic mix?
- Does the suspect deploy above actually explain it, or did it merely land nearby?
- Does an existing eval cover this, and if not, what would it have caught?

## Detection evidence

```json
{evidence}
```
"""


def describe_suspect(suspect: dict | None) -> str:
    """The deploy correlation, as prose a person can act on.

    Says so plainly when there is none. An omitted section reads as a check nobody
    performed; an explicit "no marker" reads as a check that found nothing.
    """
    if not suspect:
        return (
            "No deploy marker in the observation window, so the onset could not be "
            "correlated to a release. Triage starts from the metric alone."
        )
    return (
        f"**`{suspect['ref']}`** (`{suspect['sha']}`), released by "
        f"{suspect['released_by']}, was the most recent deploy at or before the first "
        f"breaching observation.\n\n"
        f"This is a **lead, not a conclusion**. It is the last release that landed "
        f"before the excursion began; whether it caused it is the first thing to check "
        f"and the first thing to be wrong about."
    )


def next_change_id(existing: set[str]) -> str:
    """Sequential within the year. A real deployment takes this from the ITSM."""
    numbers = [int(cid.split("-")[-1]) for cid in existing if cid.startswith("CHG-2026-")]
    return f"CHG-2026-{max(numbers, default=0) + 1:06d}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-detection", required=True)
    parser.add_argument("--outdir", default="intent")
    args = parser.parse_args()

    detection = json.loads((gate.ROOT / args.from_detection).read_text())
    change_id = next_change_id({a.change_id for a in artifacts.all_artifacts()})

    body = TEMPLATE.format(
        change_id=change_id,
        metric=detection["metric"],
        sigma=detection["latest_sigma"],
        latest=detection["latest"],
        mean=detection["mean"],
        stdev=detection["stdev"],
        rules="\n".join(f"- {r}" for r in detection["rules_fired"]) or "- (none)",
        suspect=describe_suspect(detection.get("suspect_deploy")),
        evidence=json.dumps(detection, indent=2),
    )

    slug = detection["metric"].replace("_", "-")
    path = pathlib.Path(args.outdir) / f"{change_id}-{slug}-anomaly.md"
    path.write_text(body)
    print(f"wrote {path}")

    # The artifact this script just produced must satisfy the same gate as any other.
    errors = artifacts.parse(gate.ROOT / path).errors
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

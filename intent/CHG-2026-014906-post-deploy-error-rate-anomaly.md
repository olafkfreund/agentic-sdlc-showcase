---
change_id: CHG-2026-014906
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

# Intent: post_deploy_error_rate anomaly at 6.926 sigma

> Raised by the deterministic detector in `scripts/detect_anomaly.py`. **No human was
> in the invocation path.** A human triages this: fix now, schedule, or dismiss.
> Dismissals tune the bands.

## Problem

`post_deploy_error_rate` reached **0.0271**, which is **6.926 standard deviations** from its
30-day rolling baseline of 0.011627 (sd 0.002234).

Rules fired:

- rule_1: one point beyond 3 sigma

## Suspect deploy

**`v2.7.0`** (`3f8b41d`), released by release-manager, was the most recent deploy at or before the first breaching observation.

This is a **lead, not a conclusion**. It is the last release that landed before the excursion began; whether it caused it is the first thing to check and the first thing to be wrong about.

## Who is affected

Determined at triage. The metric is a service-level signal; the population behind it
is not known to the detector and the detector does not guess.

## Success criteria

1. `post_deploy_error_rate` returns to within one sigma of its baseline and stays there for 48 hours.
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
{
  "control_id": "OPS-01",
  "gate": "anomaly_detection",
  "result": "pass",
  "findings": [],
  "timestamp": "2026-08-28T13:51:22.434140+00:00",
  "commit": "ac2ceb0944f31f562defc24d4962c09dfcfedb06",
  "run_id": "33177297961",
  "actor": "olafkfreund",
  "tier": "3sigma",
  "rules_fired": [
    "rule_1: one point beyond 3 sigma"
  ],
  "mean": 0.011627,
  "stdev": 0.002234,
  "latest": 0.0271,
  "latest_sigma": 6.926,
  "suspect_deploy": {
    "index": 9,
    "ref": "v2.7.0",
    "sha": "3f8b41d",
    "released_by": "release-manager",
    "onset_index": 9,
    "observations_before_breach": 9
  },
  "action": "propose",
  "metric": "post_deploy_error_rate",
  "autonomy_tier": "A2"
}
```

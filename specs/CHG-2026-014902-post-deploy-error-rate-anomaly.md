---
change_id: CHG-2026-014902
risk_class: R3
autonomy_tier: A2
controls: [CHG-04, TRC-01, OPS-01]
data_classification: internal
originator: svc-agent-platform@example.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
incident_id: null
---


# Spec: make a detected anomaly diagnosable

## Summary

The detector found a 6.9σ excursion in `post_deploy_error_rate` and wrote it up as an
intent with no human involved. That worked. What it produced is a number and a rule name,
and the first three things a person does on receiving it — *which deploy, when did it
start, have we seen this before* — the detector already has the data to answer and does
not.

This change makes the detection record name the suspect deploy, carries that into the
generated intent, and adds the permanent eval the intent's own success criterion asks for.

## What this spec deliberately does not do

**It does not fix the error rate.** The anomaly comes from
`ops/fixtures/post_deploy_error_rate.json`, a seeded fixture that exists so the Stage 6
walkthrough is reproducible. There is no production incident and no root cause to find.

Inventing one would be the worse failure. A spec that fabricates a cause because the
template has a section for it is how a chain of artifacts becomes decorative — every
document present, none of them load-bearing. The honest read of this intent is that the
detector is right, the finding is synthetic, and the *useful* work it exposes is that
diagnosis starts colder than it needs to.

That reading is itself a Stage 6 triage outcome: not "fix now", not "dismiss", but
"schedule — the signal is fine, the handoff is thin".

## Requirements

| # | Requirement | Traces to |
|---|---|---|
| R1 | The detection record names the deploy in scope at the first breaching observation | Intent open question: *which deploy correlates with the onset?* |
| R2 | The generated `intent.md` names that deploy, so triage starts with a suspect | Intent success criterion 2 |
| R3 | A permanent eval covers this class of anomaly | Intent success criterion 3; Stage 4.6 |
| R4 | Correlation is deterministic and unit-tested, like detection | Stage 6.2, principle 4 |

## Design

Deploy markers travel **with the metric window**, not out of band. The observability
query that returns 30 days of `post_deploy_error_rate` also knows which release was live
at each point; the fixture gains the same shape, so the demo and production differ in
where the data comes from and not in what the code does.

Correlation is then arithmetic over two arrays: find the first observation whose z-score
breaches, take the last deploy marker at or before it. One function, no lookup, no clock.

```
recent   [ . . . . . x x x ]     x = breaching
deploys  [ A . . . B . . . ]     suspect = B
```

**Rejected: query the deployments API at detection time.** It makes a deterministic,
unit-testable script depend on a network call and on GitHub being reachable, to learn
something the metrics source already knows. Detection failing because an API is slow is
worse than detection without a deploy name.

**Rejected: correlate on wall-clock timestamps.** `Date.now()` in a detector makes the
demo unreproducible and the tests time-dependent. Index positions are enough — the metric
series is already ordered.

**Rejected: have the agent identify the deploy.** No model in detection (§Stage 6.2). The
agent may reason about the suspect once it is named; it may not be what names it.

## Data

No personal data. Deploy markers are release refs and commit shas, classified internal.

## Policy conflicts

None identified. This change touches only detection and the artifact it generates; it
adds no data class, no endpoint and no external dependency.

## Non-functional

Correlation must not make detection slower or able to fail: it is pure arithmetic over
data already in hand, and a window with no deploy markers yields `null` rather than an
error. A detector that can fail is a detector that will be switched off.

## Test strategy

Unit tests for correlation alongside the existing detection tests: a deploy before the
breach, a deploy after it (must not be blamed), several deploys, no deploys at all, and
the shipped fixture. The eval case is verified by the existing runner.

---
name: plan-author
description: Draft a plan.md before implementing anything. Use at the start of every build
  task, before the first edit.
version: 1.0.0
policy_owner: Head of Engineering
paired_gate: scripts/check_plan_conformance.py
control: TRC-01
stage: 3
---

# Authoring a plan

Stage 3. Nothing gets implemented without an accepted written plan. The plan is what a
reviewer reads to decide whether the change does what was intended — reviewer attention
moves from "is this line correct" to "is the residual risk acceptable".

## Draft before any edit

`plans/<change_id>-<slug>.md`, same `change_id` as the spec.

```
## Approach       what you will do and why, in a paragraph
## Files          <- machine-read by the gate. Every path you will touch, in backticks.
## Sequence       ordered steps, each with the check that proves it worked
## Risks          what could break, ranked, with the mitigation for each
## Rejected       alternatives considered and why they lost
## Tests          the tests that will prove this change, named
## Rollback       how this is undone
```

The `## Files` section is parsed by `scripts/check_plan_conformance.py`. A code file in
the diff that no plan claims fails the build. Use one bullet per path:

```
## Files
- `service/app/main.py`
- `service/tests/test_api.py`
```

## Before you accept the plan

Interrogate it: what could this break, which step carries the most risk, what
alternatives were rejected and why. Iterate until an engineer who never saw the
conversation could implement from the plan alone. Then commit it.

## While implementing

Where the implementation departs from the plan, **update `plans/` in the same commit**.
This is enforced by the gate, not by discipline. A plan that no longer matches the diff
is worse than no plan: it is a control that reads as operating while it is not.

## Autonomy

Set `autonomy_tier` no higher than `policy/autonomy-matrix.yaml` allows for this risk
class and target environment. The gate rejects the change otherwise, and the matrix is
published precisely so this is not a negotiation.

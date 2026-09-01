---
change_id: CHG-2026-014914
risk_class: R3
autonomy_tier: A2
controls: [TRC-01, CHG-04, HUM-14]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---

# Spec: allocate against what is reserved, and never lose the finding

## Requirements

### R1 — The allocator sees ids it cannot see today

`next_change_id` stays a pure function over a set of ids, because that is what makes it
testable. What changes is who fills the set: a new `reserved_change_ids()` collects ids
from git refs — local and remote, `stage6/*` included — and `main()` unions that with the
artifact ids before allocating.

Refs are the right source rather than the GitHub issues API: refs need no token, work
offline for a person running the script locally, and a branch is what the push will
actually collide with. An id in an issue but not on a branch collides with nothing.

Where git is unavailable or the remote cannot be reached, the function returns what it
found and does not fail. A degraded allocation is recoverable; a detector that will not
run because it could not reach a remote is the failure this whole change is about.

### R2 — The fallback stops sitting behind the step most likely to fail

In `06-operate.yml`, the push is no longer permitted to end the step. If it fails, the run
still opens the issue, and the issue says the branch could not be pushed and why. The
detection is the valuable artifact; the branch is a convenience.

This is the same principle as `gate.report()` — a control that cannot complete says so
loudly rather than exiting quietly, and the finding reaches a human either way.

### R3 — Belt and braces on the branch name

If the computed branch somehow already exists on the remote, the step suffixes the run
number rather than pushing into it. R1 should make this unreachable; it is one line, and
the cost of being wrong about that is another silent night.

### R4 — A test that fails when this regresses

`scripts/tests/test_draft_intent.py` asserts that an id present only in the reserved set —
not in any artifact — is still skipped. That is precisely the case that broke, and it is
the assertion that would have caught it.

## Policy conflicts

None, but one is worth stating so it is not lost. This change touches
`.github/workflows/`, which `policy/risk-classes.yaml` floors at **R3**. The matrix
permits at most **A2 in development** at R3, so this is declared R3/A2 and goes through the
PR gate like anything else. `HUM-14` refused an earlier change in this repository for
claiming R2 while touching this path; the floor exists exactly so that a change to the
control layer cannot be self-declared as routine.

Nothing here grants Actions the ability to open or approve a pull request. The fallback is
being made reachable, not unnecessary.

## Verification

- `make build test lint gates` — TRC-01 and HUM-14 in particular.
- The new test fails against the current allocator and passes after the change.
- Stage 6 dispatched and watched to completion, with the allocated id shown to be one that
  no existing branch holds.

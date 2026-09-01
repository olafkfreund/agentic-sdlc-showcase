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

# Intent: the detector fires, allocates an id that is already taken, and loses the finding

## Problem

Stage 6 has failed on its nightly schedule since 30 August 2026 — three consecutive
nights — at the step `Open it as a pull request`. In that time it detected nothing new,
told nobody, and opened no issue. The detector itself worked perfectly every night.

The last successful run and the first failing run are **on the same commit**, `9934e84`.
Nothing was deployed between them. This is state, not code, and the first diagnosis of it
— that the failure came from bumping the actions off Node 20 in `e283613` — was wrong,
inferred from the timing and not from evidence.

**The actual cause.** `draft_intent.py::next_change_id` takes the maximum over
`artifacts.all_artifacts()`, which reads the files in the working tree. On a CI checkout
that is `main` and only `main`. Every id the detector has ever allocated lives on a
`stage6/*` branch that Actions is not permitted to merge — deliberately, because that is
the segregation of duties this repository is built on.

So the allocator cannot see its own previous output. Each night it re-derives the same
next id from `main`, builds `stage6/CHG-2026-014912`, and pushes a branch that already
exists with different history. The push is rejected. The step exits there — and because
`gh pr create` and the `gh issue create` fallback both come *after* the push, the
carefully designed fallback never runs at all.

**Two failures, one cause.** The same allocator produced a collision by hand three hours
ago: `CHG-2026-014912` was chosen for the playbook v1.1 change by listing `intent/` on
`main`, and it was already taken by the detector. That was renumbered to 014913 under
`CHG-2026-014913`. The fix belongs in the allocator both callers share, not in either
caller.

**It is about to look fixed, and will not be.** Merging 014913 pushed `main`'s maximum
past the stuck branch, so tonight's run will allocate 014914, push cleanly and go green.
The bug is untouched. It returns the next time a `stage6/` branch sits unmerged for a
day, which is the normal state of an untriaged finding.

## Who is affected

- Anyone relying on Stage 6 to surface a production anomaly. For three nights it did not.
- Whoever next allocates a change id by hand, who has no way to know what is reserved.
- The claim in §7 and on the showcase site that the loop closes without a human in the
  invocation path. For three nights it closed onto the floor.

## Success criteria

1. An id is never allocated twice, whether by the detector or by a person.
2. A push failure in Stage 6 still gets the finding to a human. The fallback must not sit
   behind the step most likely to fail.
3. The allocator has a test that fails if it stops considering reserved ids.
4. Stage 6 runs green on dispatch, and the run demonstrably could not have collided.

## Out of scope

- Stopping the detector re-raising the same ongoing anomaly nightly. That is real noise and
  a real design question, but it is a separate change with its own record.
- Merging or closing the two stranded `stage6/*` branches. They are untriaged findings and
  triage is a human's call, not a side effect of a bug fix.

## Constraints

- Actions must still be unable to open or approve a pull request. The fallback exists
  because that setting is deliberate; the fix must not quietly remove the reason for it.

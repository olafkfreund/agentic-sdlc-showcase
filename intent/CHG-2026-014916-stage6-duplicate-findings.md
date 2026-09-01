---
change_id: CHG-2026-014916
risk_class: R3
autonomy_tier: A2
controls: [TRC-01, CHG-04, HUM-14]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---

# Intent: one anomaly should be one finding, however many nights it lasts

## Problem

Stage 6 re-raises an ongoing excursion every night. It does not ask whether the thing it
found is already being tracked; it draws the same conclusion from the same data and files
it again.

The evidence is unambiguous. `CHG-2026-014911`, `014912` and `014915` — issues #7, #8
and #10 — each recorded **6.926 sigma** on `post_deploy_error_rate`. Identical readings of
an unchanged fixture, filed as three separate findings, each with its own change id, its own
branch and its own issue. All three were dismissed together as one finding counted three
times.

Both proposing paths do it, which is easy to miss: `diagnose` at 2 sigma and `propose` at
3 sigma each create an issue unconditionally.

**Why this matters more than tidiness.** A finding that appears every night stops being read.
The response is a filter rule, and then the one night the reading changes materially, nobody
notices — the detector is still perfect and the control has failed anyway. §8.5 names this
as ASI09, human-agent trust exploitation: the failure is not a hostile agent, it is a
competent one trusted into the background. A duplicate-generating detector manufactures that
outcome directly.

It also puts a number on the cost. Left alone, this produces roughly 365 issues, 365
branches and 365 change ids a year for one unfixed problem, in a repository whose §6.2 claim
is that the change id is a reliable join key.

## Who is affected

- Anyone on the receiving end of Stage 6, who currently gets a duplicate every morning.
- The change id sequence, which burns an id per night per ongoing anomaly.
- The argument on the showcase site that the loop closes cleanly without a human in the
  invocation path. It closes; it just closes repeatedly onto the same spot.

## Success criteria

1. An excursion that is already tracked by an open Stage 6 finding does not create a second
   one, at either tier.
2. When the tracked finding is closed and the metric breaches again, a new finding is
   created. Suppression must not become silence.
3. The suppression is visible: a run that suppressed something says so, and names what it
   deferred to.
4. The decision is deterministic. No model decides whether two findings are the same.

## Out of scope

- Changing the detection bands or the fixture. The detector is right; what it does with
  being right is what changes.
- Auto-closing a finding when the metric recovers. That is a triage decision with a human
  in it, and inferring "resolved" from a metric returning to baseline is exactly the kind of
  conclusion this repository does not let a machine draw unsupervised.
- Deduplicating across *different* metrics. Two metrics breaching together are two findings,
  and deciding they share a cause is diagnosis, not detection.

## Constraints

- Detection stays deterministic and model-free (§4, principle 4).
- Suppression must fail open. If the lookup cannot run, the finding gets raised. A duplicate
  is an annoyance; a suppressed real anomaly is the failure mode being introduced.

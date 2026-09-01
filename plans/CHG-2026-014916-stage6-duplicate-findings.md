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

# Plan: one lookup, in detection, gating both consumers

## Approach

One new output on `detect`, one new `if:` clause on each of the two jobs that raise
findings. No new script, no new action, no shared state.

## Files

- `scripts/detect_anomaly.py`
- `scripts/tests/test_detect_anomaly.py`
- `.github/workflows/06-operate.yml`

## Sequence

1. Emit `metric` from `detect_anomaly.py`'s output block; extend its test.
   → verify: test asserts the key is present.
2. Add the `existing_finding` lookup step to `detect`, with `issues: read`.
   → verify: YAML parses, `bash -n` clean on the step body.
3. Gate `diagnose` and `propose` on it; write the suppression line to the step summary.
   → verify: both `if:` expressions still admit the no-existing-finding case.
4. `make build test lint gates`. → verify: green; HUM-14 content with R3/A2.
5. Dispatch with a finding open. → verify: suppressed, summary names it.
6. Close it, dispatch again. → verify: raised. **This is the step that matters** — a
   suppression that never re-arms is the defect this change could introduce.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Suppression swallows a real anomaly | **high impact** | Fails open; matches open issues only; step 6 tests re-arming explicitly |
| A silent skip looks like a broken detector | high | Every suppression writes to the step summary naming the issue |
| Title matching misses, and duplicates continue | medium | Wrong in the safe direction — it degrades to today's behaviour, not to silence |
| A judgement call creeps into detection | low | Label plus substring, no scoring, no model. Principle 4 |
| Declared R2 and refused | high if careless | R3 for the workflow path floor; A2 is the matrix maximum |

## Rejected

- **A nightly "still firing" comment on the open issue.** Better than a new issue, still 365
  notifications a year for one problem. The issue being open already says it is unresolved.
  Worth revisiting if a responder actually wants a heartbeat; it should not be assumed.
- **Auto-closing when the metric recovers.** Inferring "resolved" from a number returning to
  baseline is a diagnosis, and a machine does not get to make it unsupervised here.
- **Deduplicating in `draft_intent.py`.** By then the branch and the id are already
  allocated. The cheapest place to not do work is before doing it.
- **Similarity matching across findings.** Puts a judgement in detection. Principle 4.
- **Doing this inside `CHG-2026-014914`.** It would have masked whether that fix worked,
  which is why it was deferred rather than bundled.

## Tests

- `scripts/tests/test_detect_anomaly.py` — metric emitted
- `make build test lint gates`, `make negative`
- Two dispatches: suppressed, then re-armed

## Rollback

Revert. Stage 6 returns to raising a finding per run, which is the current behaviour.

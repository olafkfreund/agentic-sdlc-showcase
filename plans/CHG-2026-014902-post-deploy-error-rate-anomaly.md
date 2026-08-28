---
change_id: CHG-2026-014902
risk_class: R3
autonomy_tier: A2
controls: [CHG-04, TRC-01, OPS-01]
data_classification: internal
originator: svc-agent-platform@example.com
agent_identity: svc-agent-platform
model_route: gateway/tier-balanced
supersedes: null
incident_id: null
---

# Plan: make a detected anomaly diagnosable

## Approach

Deploy markers ride along with the metric window. Correlation becomes one pure function
over two arrays — first breaching index, last marker at or before it — which keeps the
detector free of clocks, network calls and models, and keeps it unit-testable the way
Stage 6.2 requires.

Build the function and its tests before touching the fixture or the intent template, so
the tests fail for the right reason first.

## Files

- `scripts/detect_anomaly.py`
- `scripts/draft_intent.py`
- `scripts/tests/test_detect_anomaly.py`
- `ops/fixtures/post_deploy_error_rate.json`
- `.agent/evals/cases/024-anomaly-names-the-suspect-deploy.yaml`
- `.github/workflows/06-operate.yml`
- `specs/CHG-2026-014902-post-deploy-error-rate-anomaly.md`
- `plans/CHG-2026-014902-post-deploy-error-rate-anomaly.md`

## Sequence

1. `correlate(z, deploys)` in `detect_anomaly.py`, returning the suspect marker or `None`.
   → verify: new tests in `test_detect_anomaly.py` cover before/after/several/none, and
   fail before the function exists.
2. Deploy markers in the fixture, positioned so the suspect is unambiguous.
   → verify: `test_the_shipped_fixture_names_a_suspect_deploy`.
3. `evaluate()` returns the suspect; `detect_anomaly.py` writes it to the evidence record
   and to `GITHUB_OUTPUT`. → verify: `python scripts/detect_anomaly.py` prints it.
4. `draft_intent.py` names the suspect in the generated intent, and says plainly when
   there is none. → verify: generate against the fixture and read the output.
5. Eval case 024. → verify: `make eval` at 24/24.
6. `06-operate.yml` surfaces the suspect in the issue body.
   → verify: dispatch the workflow and read the issue.
7. Full loop. → verify: `make build test lint gates eval`.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Correlation blames a deploy that landed *after* the breach began | medium — it is the obvious off-by-one, and it would send triage to the wrong team | explicit test `test_a_deploy_after_the_breach_is_not_blamed`; the function takes the last marker at or **before** the first breaching index, never the nearest |
| A window with no deploy markers raises, and detection dies | low, high impact | returns `None`; the intent says "no deploy marker in the window" rather than omitting the section, so an absent correlation is visible rather than silent |
| The suspect is treated as a conclusion rather than a lead | medium | the intent labels it *suspect*, keeps the open question, and the triage sections stay |
| Adding fields to the fixture breaks the existing detection tests | low | fixture shape is additive; `evaluate()` defaults `deploys` to empty |

## Rejected

- Querying the deployments API during detection — a network dependency in a script whose
  value is that it cannot fail.
- Wall-clock correlation — makes the demo unreproducible and the tests time-dependent.
- Letting the agent identify the deploy — no model in detection.

## Tests

- `test_correlate_names_the_deploy_before_the_breach`
- `test_a_deploy_after_the_breach_is_not_blamed`
- `test_the_most_recent_prior_deploy_wins`
- `test_no_deploy_markers_yields_none`
- `test_no_breach_yields_none`
- `test_the_shipped_fixture_names_a_suspect_deploy`

## Rollback

`git revert` the merge commit. Detection reverts to reporting sigma and rule names, which
is what it does today; nothing downstream depends on the new field.

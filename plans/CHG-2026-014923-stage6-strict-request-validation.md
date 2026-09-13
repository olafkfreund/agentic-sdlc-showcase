---
change_id: CHG-2026-014923
risk_class: R3
autonomy_tier: A0
controls: [SEC-API-01, CHG-04, DP-11]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
incident_id: 14
---

# Plan: reject unknown fields and stop echoing request payloads

## Approach

Tighten the two existing request models, add a small validation-error handler, and add
focused tests for the affected endpoints. No business-logic changes, no new dependencies,
no gate changes.

## Files

- `service/app/models.py`
- `service/app/main.py`
- `service/tests/test_api.py`
- `service/tests/test_refunds.py`

## Sequence

1. Add strict `extra="forbid"` model config to the payment and refund request models.
   → verify: valid request tests continue to pass.
2. Add a request-validation handler that removes echoed `input` payloads from 422
   responses.
   → verify: schema-level validation failures still describe the error without returning
   personal fields.
3. Add one payment API test and one refund API test for unknown-field rejection.
   → verify: each new test fails before the model/handler change and passes after it.
4. Run targeted tests, then `make build test lint gates`.
   → verify: all repository checks remain green.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| A legitimate client depends on silently ignored fields | low | Reject explicitly at validation so the mismatch is visible and actionable |
| Error responses expose personal data while rejecting the body | low | Verify with focused tests that only the extra field location is named |

## Rollback

Revert the model config change, validation handler, and the two tests. No migration or
persisted data change is involved.

---
change_id: CHG-2026-014882
risk_class: R3
autonomy_tier: A2
controls: [SEC-API-01, CHG-04, DP-11]
data_classification: internal
originator: j.ortiz@example.com
agent_identity: svc-agent-platform
model_route: gateway/tier-balanced
supersedes: null
---

# Plan: refunds against a settled payment

## Approach

Add the `Refund` model, a store keyed on `payment_id` to make R2 a constraint rather than
a check, and the route. The route stays thin — validation and audit only — with the
settled-only and already-refunded decisions in the domain layer where they can be tested
without HTTP.

## Files

- `service/app/models.py`
- `service/app/main.py`
- `service/tests/test_api.py`
- `service/tests/test_refunds.py`

## Sequence

1. `RefundRequest` / `RefundResponse` models and the classification entries for
   `operator_id`. → verify: `make lint` clean, `CLASSIFICATION` covers every new field.
2. Refund store with a uniqueness constraint on `payment_id`.
   → verify: `test_refunds.py::test_second_refund_is_conflict` fails before, passes after.
3. `POST /payments/{payment_id}/refunds` with the gateway token and `audit.emit()`.
   → verify: `scripts/check_endpoints.sh` passes; it fails today if the audit call is absent.
4. The settled-only rule. → verify: `test_refunds.py::test_unsettled_payment_is_422`.
5. Full-loop check. → verify: `make build test lint gates`, output pasted into the PR.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| `operator_id` leaks into a log line during debugging | medium — this is exactly INC-2026-0431 | `check_pii.py` gate plus an explicit test; `operator_id` is in `PERSONAL_FIELDS` from step 1, before the route exists |
| Check-then-act race issues two refunds under concurrent requests | low at this volume, catastrophic if it happens | uniqueness constraint, not an `if not exists` check |
| The provider's API semantics differ from our model | medium | provider call is stubbed this change; the integration is a separate change with its own R3 record |

## Rejected

- Mutating `payment.status` in place — breaks reconciliation's append-only assumption.
- Doing this at A3 in development to move faster — the change touches `models.py`, which
  `policy/risk-classes.yaml` floors at R3 for the classification map. Kept to A2 and
  confined the model change to additive fields.

## Tests

- `test_refunds.py::test_full_refund_succeeds`
- `test_refunds.py::test_second_refund_is_conflict`
- `test_refunds.py::test_unsettled_payment_is_422`
- `test_refunds.py::test_operator_id_never_logged`
- `test_api.py::test_refund_emits_audit_event`

## Departures from this plan, recorded during implementation

Stage 3.4: where the implementation departs from the plan, the plan is updated in the
same commit. Three departures.

**1. Risk class raised R2 → R3.** The plan claimed `service/app/models.py`, which
`policy/risk-classes.yaml` floors at R3 because it holds the data classification map,
and `check_autonomy.py` refused the change. The gate was right and the plan was wrong:
this adds `operator_id`, a new **personal data** field, to that map. That is material by
any reading, and calling it standard feature work was the plan optimistically
classifying its own blast radius. `autonomy_tier` stays A2 — the matrix permits A2 for
R3 in development — so nothing else moved. Raised in the intent and spec too, so the
chain agrees with itself.

**2. A `settle()` stand-in.** R5 requires that only settled payments may be refunded,
and nothing in this service could reach the settled state, because settlement is an
external event we are told about by the provider. Rather than stub the provider — a
separate change with its own record — `main.settle()` stands in for the settlement
webhook. It is not reachable over HTTP and exists so the settled-only rule has something
to test against.

**3. `service/tests/test_api.py` gained one test** beyond the five named here
(`test_refund_emits_audit_event`), because the spec's R3 deserves a test in the API
suite as well as the refund suite. Already claimed under `## Files`.

## Rollback

`git revert` the merge commit and redeploy. No schema migration and no provider state, so
the revert is complete. Rehearsed in staging as part of the scheduled rollback drill.

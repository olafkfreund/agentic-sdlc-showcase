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

# Spec: reject unknown fields and stop echoing request payloads

## Requirements

| # | Requirement | Traces to |
|---|---|---|
| R1 | `PaymentRequest` forbids unknown fields | Success criterion 1 |
| R2 | `RefundRequest` forbids unknown fields | Success criterion 2 |
| R3 | Schema-validation failures do not echo request payload `input` values | Success criterion 3 |

## Design

Use Pydantic v2's `ConfigDict(extra="forbid")` on the two request models already used by
the write endpoints. This keeps route signatures unchanged and moves strictness into the
schema definition where FastAPI applies it consistently.

Add one FastAPI `RequestValidationError` handler that returns the validation reasons but
strips the echoed `input` payload field from each error entry. No new model is
introduced. The existing request types remain the contract; they become strict rather
than permissive, and their failures become safe to return.

## Policy conflicts

None identified. The stricter validation satisfies SEC-API-01 rule 2 without changing the
authentication, audit, or logging controls already in place.

## Verification

- Add one payment API test proving an extra body field returns 422 without echoing
  personal data.
- Add one refund API test proving an extra body field returns 422 without echoing
  personal data.
- Run the targeted tests, then `make build test lint gates`.

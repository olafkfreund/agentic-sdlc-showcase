---
change_id: CHG-2026-014882
risk_class: R3
autonomy_tier: A2
controls: [SEC-API-01, CHG-04, DP-11]
data_classification: internal
originator: j.ortiz@example.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---

# Spec: refunds against a settled payment

## Summary

Add `POST /payments/{payment_id}/refunds`, which issues a full refund against a settled
payment and records it as an auditable event attributable to the operator. Idempotent on
the payment id, so the double-payment failure mode is closed structurally rather than by
operator discipline.

## Requirements

| # | Requirement | Traces to |
|---|---|---|
| R1 | `POST /payments/{payment_id}/refunds` issues a full refund | Success criterion 1 |
| R2 | A second refund against the same payment returns 409, not a second refund | Success criterion 2 |
| R3 | The refund emits an audit event with actor, action, entity and timestamp | Success criterion 3 |
| R4 | Refunds are stored alongside payments and exposed to reconciliation | Success criterion 4 |
| R5 | Only settled payments may be refunded; others return 422 | Out of scope, made explicit |

## Design

A refund is a record, not a mutation. `POST` creates a `Refund` linked to the payment;
the payment's `status` becomes `refunded` as a derived read. This keeps the payment row
immutable, which reconciliation depends on, and makes R2 a uniqueness constraint rather
than a check-then-act race.

Idempotency is on `(payment_id)` since partial refunds are out of scope. When they arrive,
the key becomes `(payment_id, idempotency_key)` — noted so the migration is expected.

**Rejected:** mutating the payment row in place. Simpler, but reconciliation reads
payments as an append-only log and a mutable row breaks its assumptions silently.

**Rejected:** a queue-backed asynchronous refund. Correct at ten times this volume, and
premature at forty a week. Revisit above 500/week.

## Data

| Entity | Fields | Classification |
|---|---|---|
| Refund | refund_id, payment_id, amount, currency, status, created_at | internal |
| Refund | operator_id | personal — never logged, redacted per DP-11 |

Seven-year retention (STD-DATA-07) applies. No new personal data is introduced beyond
`operator_id`, which is already held for payments.

## Policy conflicts

None identified. The operator identity requirement (SEC-API-01 rule 3, audit) and the
data-protection rule (DP-11, no personal data in logs) are jointly satisfiable: the audit
event carries `actor` as the gateway-authenticated service identity, and `operator_id` is
stored in the record but redacted from every log line by `audit.redact()`.

## Non-functional

- Volume: 40/week today, plan for 500/week.
- Latency: p95 under 800ms, bounded by the provider's API.
- The provider is rate-limited to 10 rps; a single operator UI cannot approach this.
- Availability: same as payments. No separate SLO.

## Test strategy

Unit tests for the idempotency constraint and the settled-only rule. An integration test
for the full refund path. A test asserting `operator_id` never appears in a log line —
this is the one that would have caught INC-2026-0431.

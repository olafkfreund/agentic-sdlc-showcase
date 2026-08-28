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

# Intent: refunds against a settled payment

## Problem

When a customer disputes a payment, the operations team cannot reverse it in our system.
They raise a ticket with the payment provider, wait between two and five working days,
and then key the outcome into a spreadsheet so the reconciliation run picks it up. Nobody
trusts the spreadsheet. Last month two refunds were paid twice because two people worked
the same ticket.

## Who is affected

The payments operations team — six people. Roughly forty disputes a week, rising in the
weeks after a marketing campaign. Also the reconciliation team, who inherit the errors.

## Success criteria

1. An operator can issue a full refund against a settled payment from our own system.
2. A payment that has already been refunded cannot be refunded again.
3. Every refund is attributable to the operator who issued it, at the time they issued it.
4. The reconciliation run reads refunds from the same place it reads payments.

## Out of scope

- Partial refunds. Operations say these are under 5% of cases and can stay manual for now.
- Refunds against payments that have not settled. Different problem, different provider API.
- Any change to the dispute intake process itself.

## Constraints

- Refund records are subject to the seven-year retention rule (STD-DATA-07).
- The provider's refund API is rate-limited to 10 requests per second.
- Must be live before the Q4 campaign, which starts in nine weeks.

## Open questions

- Does a refund need a separate approval above a threshold value? Referred to Finance.

---
change_id: CHG-2026-014901
risk_class: R3
autonomy_tier: A2
controls: [FIN-02, DP-11, CHG-04, SEC-API-01]
data_classification: personal
originator: p.nakamura@example.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
itsm_record: https://example.service-now.com/change_request.do?sysparm_query=number=CHG-2026-014901
---


# Intent: accept payments in a currency the payer chooses

## Problem

We accept GBP, EUR and USD, and we bill in the currency the merchant is settled in. A
payer in Warsaw sees a EUR amount, their bank converts it at an unknown rate, and they
are charged something other than what they agreed to. Our support queue gets about thirty
"you charged me the wrong amount" contacts a month, and every one of them is correct.

Merchants want us to show and charge the payer's own currency, converted by us at a rate
we quote up front.

## Who is affected

Payers outside the merchant's settlement currency — currently 18% of volume and growing
as we sign merchants in central Europe. Support handles roughly thirty contacts a month.
Finance carries the FX exposure informally today with no hedging.

## Success criteria

1. A payer is quoted a total in their own currency before they confirm.
2. The amount charged equals the amount quoted, exactly.
3. The rate used and the time it was quoted are recorded against the payment.
4. Finance can report on FX exposure per settlement window.

## Out of scope

- Hedging. Finance will treat exposure separately.
- Currencies with a minor unit other than two decimal places. JPY and KWD wait for a
  follow-up; taking them now would change the money type across the service.
- Refunds in a converted currency. Follows once this settles.

## Constraints

- The quoted rate must hold for at least fifteen minutes or payers abandon checkout.
- Rate provider contract is under negotiation; assume a REST quote API with a TTL.
- Payer location is inferred from the card BIN, which is personal data.
- Live before the Q4 campaign — nine weeks.

## Open questions

- What happens if the rate expires between quote and confirm? Referred to Product.
- Who owns the residual when the settled amount differs by rounding? Referred to Finance.

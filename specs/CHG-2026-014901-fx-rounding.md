---
change_id: CHG-2026-014901
risk_class: R3
autonomy_tier: A0
controls: [FIN-02, DP-11, CHG-04, SEC-API-01]
data_classification: personal
originator: p.nakamura@example.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
itsm_record: https://example.service-now.com/change_request.do?sysparm_query=number=CHG-2026-014901
---


# Spec: payer-currency pricing with a quoted rate

> **STATUS: BLOCKED ON POLICY CONFLICT.** Two conflicts below could not be jointly
> satisfied. Per Stage 2 control point, named policy owners resolve these with the
> product owner **before engineering sees this spec**. `autonomy_tier` is A0 until they
> are closed: the agent may read and propose, and nothing else.

## Summary

Quote the payer a total in their own currency, hold that rate for the checkout window,
charge exactly the quoted amount, and record the rate and its timestamp against the
payment so Finance can report exposure.

## Requirements

| # | Requirement | Traces to |
|---|---|---|
| R1 | Quote a total in the payer's currency before confirmation | Success criterion 1 |
| R2 | The amount charged equals the amount quoted, to the minor unit | Success criterion 2 |
| R3 | Rate, provider and quote timestamp recorded against the payment | Success criterion 3 |
| R4 | FX exposure reportable per settlement window | Success criterion 4 |
| R5 | A quote expires after its TTL and cannot be confirmed | Constraint |

## Design

A `Quote` entity holds the source and target amounts, the rate, the provider, the quote
time and the TTL. Confirmation references a quote id; the charge is the quote's target
amount, taken verbatim rather than recomputed. Recomputing at confirm time is how the
charged amount drifts from the quoted one.

Conversion happens once, at quote time, using `Decimal` throughout with the rate held at
the provider's full precision and the *result* quantised to the target currency's minor
unit. Quantising the rate first loses money at volume.

**Rejected:** converting at confirm time. Simpler, and it breaks R2 the first time the
market moves between quote and confirm.

## Data

| Entity | Fields | Classification |
|---|---|---|
| Quote | quote_id, source/target amount and currency, rate, provider, quoted_at, ttl | internal |
| Quote | payer_country (from card BIN) | **personal** |

## Policy conflicts

### Conflict 1 — rate provenance versus data minimisation

- **STD-FIN-11 (Finance Control Standard), owner: Group Financial Controller.** Every
  converted transaction must retain the full rate quotation payload from the provider for
  seven years, so a disputed conversion can be reconstructed exactly as quoted.
- **STD-DATA-04 (Data Protection Standard), owner: Data Protection Officer.** Personal
  data is retained only as long as necessary for the stated purpose. The payer's inferred
  country and the BIN-derived attributes in the provider payload are personal data, and
  the stated purpose expires at settlement.

**Why they cannot both hold.** The provider's quotation payload embeds the BIN-derived
attributes used to select the rate. Retaining the payload for seven years retains
personal data for seven years. Redacting it before storage means the retained artifact is
no longer the payload as quoted, which is what STD-FIN-11 exists to preserve.

**Options.**

| | Option | Trade-off |
|---|---|---|
| A | Retain the full payload for seven years | Satisfies STD-FIN-11. Requires a DPIA and a lawful basis for seven-year retention of BIN-derived personal data; the DPO's initial view is that legitimate interest will not stretch that far. |
| B | Store a redacted payload plus a cryptographic hash of the original | Satisfies STD-DATA-04. STD-FIN-11's reconstruction requirement is met only if the provider retains the original and remains contractable for seven years — which the contract under negotiation does not currently say. |
| C | Ask the provider for a quotation payload that carries no BIN-derived fields | Satisfies both, if the provider will do it. Commercial question, not a technical one. Blocks on the contract negotiation already in flight. |

**Not resolved here.** Requires the Group Financial Controller and the DPO together.
Option C is the only one that satisfies both standards and is the one to put to the
provider while the contract is open — but that is their call, not this spec's.

### Conflict 2 — quote hold versus fair-pricing

- **STD-FIN-11.** A quoted rate held longer than five minutes must carry a documented
  spread justification, because a held rate is an implicit option written to the payer.
- **Intent constraint.** The quoted rate must hold for at least fifteen minutes or payers
  abandon checkout.

**Why they cannot both hold as stated.** Fifteen minutes exceeds the five-minute
threshold, so the spread justification becomes mandatory — and no spread has been
proposed, because the intent assumes we pass the provider's rate through unchanged. A
pass-through rate held for fifteen minutes is an unhedged fifteen-minute option written
to every payer, which is the exposure the standard exists to price.

**Options.** (A) hold five minutes and accept the abandonment cost; (B) hold fifteen
minutes with a documented spread, changing the pricing proposition; (C) hold fifteen
minutes unhedged with a board-level exposure limit.

**Not resolved here.** Group Financial Controller, with Product on the abandonment data.

## Non-functional

Quote latency p95 under 400ms including the provider call. Quote volume roughly 3x
payment volume. Provider outage must fail closed to the settlement currency, never to a
stale rate.

## Test strategy

Property test that quoted total equals charged total across a generated rate and amount
matrix. A test that an expired quote cannot be confirmed. A test that no BIN-derived
field reaches a log line. FX arithmetic tested against Finance's worked examples.

## Not yet written

`plans/CHG-2026-014901-fx-rounding.md` does not exist and must not be written until both
conflicts are closed. The chain stops here by design — which is the point of Stage 2.

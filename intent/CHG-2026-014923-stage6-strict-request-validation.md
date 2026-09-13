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

# Intent: reject unknown fields and stop echoing request payloads

## Problem

The weekly Stage 6 scan's Pass 2 review found two linked problems on the payment write
endpoints. First, the request models silently accept unknown fields. Second, FastAPI's
default schema-validation response echoes attacker-supplied `input`, which can include
fields classified `personal`.

Together, that violates `.agent/skills/secure-api-review/SKILL.md`: rule 2 requires
unknown fields to be rejected, and rule 5 requires returning the reason rather than the
payload.

## Who is affected

- API clients, whose request mistakes are currently accepted instead of surfaced.
- Reviewers relying on the secure API standard to mean "typed and strict", not merely
  "typed".
- Anyone investigating an incident, because silent acceptance makes malformed requests
  harder to distinguish from correct ones.

## Success criteria

1. `POST /payments` rejects request bodies containing keys outside `PaymentRequest`.
2. `POST /payments/{payment_id}/refunds` rejects request bodies containing keys outside
   `RefundRequest`.
3. Schema-validation failures do not echo personal request data back in the 422 body.

## Out of scope

- Expanding the deterministic endpoint gate to inspect Pydantic `extra` configuration.
- Any change to authentication, audit emission, or response schemas.

## Constraints

- Keep the change within the existing FastAPI/Pydantic v2 pattern.
- Preserve current behavior for valid requests and existing tests.

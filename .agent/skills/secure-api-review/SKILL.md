---
name: secure-api-review
description: Apply the organisation's API security standard. Use whenever creating or
  modifying an external-facing endpoint, reviewing API code, or generating an OpenAPI
  specification.
version: 1.2.0
policy_owner: Head of Application Security
source_of_truth: STD-SEC-API v4 (internal standards library)
paired_gate: scripts/check_endpoints.sh
control: SEC-API-01
---

# Secure API review

When creating or changing an API endpoint:

1. **Authentication** — every endpoint requires the gateway token (`x_gateway_token`).
   No anonymous routes outside `/health`.
2. **Input validation** — validate request bodies against a typed Pydantic model and
   reject unknown fields. Never accept a bare `dict`.
3. **Audit** — every state-changing endpoint (`POST`/`PUT`/`PATCH`/`DELETE`) emits an
   audit event via `audit.emit()` carrying actor, action, entity and timestamp.
4. **Data classification** — fields marked `personal` in `service/app/models.py` must
   never appear in logs or error messages. Log through `audit.safe_log()`.
5. **Error messages** — return the reason, never the payload. An error that echoes the
   request body is a data-protection incident with a 200-line stack trace attached.

Run `scripts/check_endpoints.sh` and include its literal output in your summary.

The paired deterministic gate runs the same script in CI and fails the build. This
skill makes violations rare; the gate makes them impossible.

#!/usr/bin/env bash
# SEC-API-01 — the paired deterministic gate for the secure-api-review skill.
#
# Playbook Appendix B: "The skill makes violations rare; the gate makes them
# impossible." This is that gate. It is intentionally a shell script, because the
# skill tells the agent to run scripts/check-endpoints.sh and include the output.
set -euo pipefail
cd "$(dirname "$0")/.."
exec "${PY:-python3}" scripts/check_endpoints.py "$@"

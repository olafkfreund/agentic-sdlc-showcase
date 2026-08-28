#!/usr/bin/env bash
# Prove every gate refuses.
#
# A gate that has never refused anything is indistinguishable from a gate that
# cannot. This script breaks the thing each gate protects, asserts the gate goes
# red, and restores the tree. It is the honest half of `make gates`.
#
#   make negative
set -uo pipefail
cd "$(dirname "$0")/../../.."
PY="${PY:-.venv/bin/python}"
[ -x "$PY" ] || PY=python3

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "working tree is dirty; commit or stash first (this script edits files)" >&2
  exit 2
fi

PASS=0; FAIL=0
restore() { git checkout -q -- . 2>/dev/null; git clean -qfd service scripts policy plans 2>/dev/null; }
trap restore EXIT

# expect_red <name> <gate-command> ; the breakage is applied by the caller first
expect_red() {
  local name="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "  DID NOT REFUSE  $name"; FAIL=$((FAIL+1))
  else
    echo "  refused         $name"; PASS=$((PASS+1))
  fi
  restore
}

echo
echo "Negative tests — each gate must refuse:"
echo

# FIN-02 — a float on a monetary field
printf '\ndef broken(amount: float) -> float:\n    total: float = 0.0\n    return round(total)\n' >> service/app/money.py
expect_red "FIN-02  float on a monetary field" "$PY" scripts/check_money.py

# DP-11 — a personal field in an error message
"$PY" - <<'PY'
import pathlib
p = pathlib.Path("service/app/main.py")
p.write_text(p.read_text().replace(
  "raise HTTPException(status_code=422, detail=str(exc)) from exc",
  "raise HTTPException(status_code=422, detail=request.payer_email) from exc"))
PY
expect_red "DP-11   personal data in an error message" "$PY" scripts/check_pii.py

# DP-11 — logging outside the sanctioned path
printf '\nimport logging\n\ndef leak():\n    logging.getLogger("x").info("payer")\n' >> service/app/main.py
expect_red "DP-11   logging outside audit.safe_log()" "$PY" scripts/check_pii.py

# SEC-API-01 — a state-changing route with no auth, no audit, no typed body
cat >> service/app/main.py <<'EOF'


@app.post("/refunds")
def create_refund(body: dict) -> dict:
    return {"ok": True}
EOF
expect_red "SEC-API-01  unauthenticated, unaudited POST" bash scripts/check_endpoints.sh

# FRZ-01 — an edit to a frozen path
echo "# an unauthorised edit" >> service/app/v1_legacy/__init__.py
git add -A >/dev/null 2>&1
expect_red "FRZ-01  edit to a frozen path" "$PY" scripts/check_frozen_paths.py
git reset -q >/dev/null 2>&1; restore

# SOD-01 — a CODEOWNERS rule guarding a path that no longer exists.
# GitHub silently ignores it, so the rule reads as configured and requires nobody.
echo "/does/not/exist/  @olafkfreund" >> CODEOWNERS
expect_red "SOD-01  CODEOWNERS rule guarding a missing path" "$PY" scripts/check_codeowners.py

# SOD-01 — the control layer left to the catch-all rule
"$PY" - <<'PY'
import pathlib, re
p = pathlib.Path("CODEOWNERS")
p.write_text(re.sub(r"^/policy/\s+\S+$", "", p.read_text(), flags=re.M))
PY
expect_red "SOD-01  control layer with no named owner" "$PY" scripts/check_codeowners.py

# CHG-04 — an artifact with no header
echo "# no header" > intent/CHG-2026-999999-bad.md
expect_red "CHG-04  artifact with no header" "$PY" scripts/check_artifact_header.py
rm -f intent/CHG-2026-999999-bad.md

# CHG-04 — a raw model name where a route belongs
"$PY" - <<'PY'
import pathlib
p = pathlib.Path("plans/CHG-2026-014882-refund-endpoint.md")
p.write_text(p.read_text().replace("model_route: gateway/tier-balanced",
                                   "model_route: some-frontier-model-v3"))
PY
expect_red "CHG-04  raw model name instead of a route" "$PY" scripts/check_artifact_header.py

# HUM-14 — autonomy above what the matrix allows for the risk class
"$PY" - <<'PY'
import pathlib
p = pathlib.Path("plans/CHG-2026-014880-showcase-scaffold.md")
p.write_text(p.read_text().replace("autonomy_tier: A2", "autonomy_tier: A3", 1))
PY
expect_red "HUM-14  R3 change claiming A3 autonomy" "$PY" scripts/check_autonomy.py

# HUM-14 — a material change self-declaring as routine.
# The floor comes from the paths actually touched, so the test has to touch one:
# models.py holds the data classification map and is floored at R3.
"$PY" - <<'PY'
import pathlib, re
p = pathlib.Path("plans/CHG-2026-014882-refund-endpoint.md")
# Whatever it declares today, declare it routine. The floor comes from the paths.
p.write_text(re.sub(r"^risk_class: R\d$", "risk_class: R1", p.read_text(), count=1, flags=re.M))
PY
printf '\n# a change to the classification map\n' >> service/app/models.py
git add -A >/dev/null 2>&1
expect_red "HUM-14  material change declared R1" "$PY" scripts/check_autonomy.py
git reset -q >/dev/null 2>&1; restore

# TRC-01 — code changed that no plan claims
"$PY" - <<'PY'
import pathlib
p = pathlib.Path("plans/CHG-2026-014880-showcase-scaffold.md")
p.write_text(p.read_text().replace("- `service/**`\n", ""))
PY
printf '\n# an unplanned change\n' >> service/app/audit.py
git add -A >/dev/null 2>&1
expect_red "TRC-01  code changed with no plan claiming it" "$PY" scripts/check_plan_conformance.py
git reset -q >/dev/null 2>&1; restore

echo
echo "  $PASS refused, $FAIL did not."
echo
[ "$FAIL" -eq 0 ] || exit 1

#!/usr/bin/env bash
# Prove the Substitution Test holds under every runtime.
#
# The claim is that the agent runtime is the most replaceable component in the system.
# This switches to each one in turn and re-scores the repository — the deterministic
# gates, the eval suite and the Substitution Test — restoring the original selection
# at the end. If any score moves, the claim was decoration.
#
#   make swap
set -uo pipefail
cd "$(dirname "$0")/../../.."
PY="${PY:-.venv/bin/python}"
[ -x "$PY" ] || PY=python3

if ! git diff --quiet -- .agent/runtimes.yaml; then
  echo ".agent/runtimes.yaml is dirty; commit or stash first (this script edits it)" >&2
  exit 2
fi

ORIGINAL="$("$PY" scripts/switch_runtime.py --current)"
restore() { "$PY" scripts/switch_runtime.py "$ORIGINAL" >/dev/null 2>&1; git checkout -q -- .agent/runtimes.yaml 2>/dev/null; }
trap restore EXIT

RUNTIMES=$("$PY" - <<'PY'
import yaml, pathlib
print(" ".join(yaml.safe_load(pathlib.Path(".agent/runtimes.yaml").read_text())["runtimes"]))
PY
)

printf '\n  Scoring the repository under each agent runtime:\n\n'
printf '  %-9s  %-8s  %-7s  %-7s  %s\n' runtime gates evals subst 'cost vs HEAD'
printf '  %-9s  %-8s  %-7s  %-7s  %s\n' --------- -------- ------- ------- ------------
FAIL=0

for rt in $RUNTIMES; do
  "$PY" scripts/switch_runtime.py "$rt" >/dev/null || { echo "  cannot select $rt"; FAIL=1; continue; }

  if make gates PY="$PY" >/dev/null 2>&1; then GATES="8/8"; else GATES="FAILED"; FAIL=1; fi

  EVALS=$("$PY" .agent/evals/run.py --mode static 2>/dev/null | grep -oE '[0-9]+/[0-9]+' | tail -1)
  SUBST=$("$PY" scripts/substitution_test.py 2>/dev/null | grep -oE '[0-9]+/[0-9]+' | tail -1)
  [ "${EVALS:-}" = "24/24" ] || FAIL=1
  [ "${SUBST:-}" = "12/12" ] || FAIL=1

  # The whole diff a vendor change costs, measured rather than claimed. The runtime
  # already selected costs nothing, which is why it reads 0.
  DIFF=$(git diff --numstat -- .agent/runtimes.yaml | awk '{print $1"+ "$2"-"}')

  printf '  %-9s  %-8s  %-7s  %-7s  %s\n' "$rt" "$GATES" "${EVALS:-?}" "${SUBST:-?}" "${DIFF:-0+ 0-}"
done

printf '\n  Identical under every runtime, because none of it belongs to a vendor:\n'
printf '    %2d skills          %2d eval cases      %2d policy tables\n' \
  "$(ls .agent/skills/*/SKILL.md 2>/dev/null | wc -l)" \
  "$(ls .agent/evals/cases/*.yaml | wc -l)" \
  "$(ls policy/*.yaml | wc -l)"
printf '    %2d gates           %2d artifacts       %2d control objectives\n' \
  "$(ls scripts/check_*.py | wc -l)" \
  "$(ls intent/*.md specs/*.md plans/*.md | wc -l)" \
  "$(grep -c '^  - id:' policy/controls.yaml)"

if [ "$FAIL" -eq 0 ]; then
  printf '\n  Every runtime scores identically. The swap is one line in .agent/runtimes.yaml.\n\n'
else
  printf '\n  A score moved under a runtime change. That is a portability debt, not a refactor.\n\n'
fi
exit "$FAIL"

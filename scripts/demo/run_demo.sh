#!/usr/bin/env bash
# The demo, narrated and in order.
#
# Everything here runs against this repository. Nothing is staged, mocked, or read
# from a transcript of a previous run — which is the only reason it is worth showing.
#
#   just demo            the full sequence, pausing between acts
#   just demo --fast     no pauses, for a recording or CI
#   just demo --live     also touches GitHub (needs `gh auth login`)
#
# Exits non-zero if any act fails, so a broken demo fails in rehearsal rather than
# in front of the audience.
set -uo pipefail
cd "$(dirname "$0")/../.."

PY="${PY:-.venv/bin/python}"
[ -x "$PY" ] || PY=python3
PAUSE=1
LIVE=0
for arg in "$@"; do
  case "$arg" in
    --fast) PAUSE=0 ;;
    --live) LIVE=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

# Colour only when a human is watching; a redirected log gets clean text.
if [ -t 1 ]; then
  B=$'\e[1m'; DIM=$'\e[2m'; ORANGE=$'\e[38;5;208m'; GREEN=$'\e[38;5;142m'; R=$'\e[0m'
else
  B=""; DIM=""; ORANGE=""; GREEN=""; R=""
fi

FAILED=0
ACT=0

act() {
  ACT=$((ACT + 1))
  printf '\n%s%s──────────────────────────────────────────────────────────────%s\n' "$ORANGE" "$B" "$R"
  printf '%s%s  Act %d · %s%s\n' "$ORANGE" "$B" "$ACT" "$1" "$R"
  printf '%s%s──────────────────────────────────────────────────────────────%s\n\n' "$ORANGE" "$B" "$R"
  shift
  for line in "$@"; do printf '  %s%s%s\n' "$DIM" "$line" "$R"; done
  [ $# -gt 0 ] && echo
  return 0
}

say() { printf '  %s%s%s\n\n' "$DIM" "$1" "$R"; }

run() {
  printf '  %s$ %s%s\n\n' "$B" "$*" "$R"
  if "$@"; then return 0; fi
  printf '\n  %sACT %d FAILED: %s%s\n' "$ORANGE" "$ACT" "$*" "$R"
  FAILED=1
  return 1
}

beat() {
  [ "$PAUSE" -eq 1 ] || return 0
  [ -t 0 ] || return 0
  printf '\n  %s[enter]%s' "$DIM" "$R"
  read -r _ || true
  printf '\r                \r'
}

# ---------------------------------------------------------------------------------

printf '\n%s%s  The Agentic SDLC, as code that runs%s\n' "$B" "$GREEN" "$R"
say "Seven stages, five planes, gates that refuse, evidence as a by-product."
beat

act "The closed loop" \
    "The same four commands AGENTS.md tells the agent to run. If CI and the" \
    "agent's loop diverge, the agent is optimising for the wrong signal."
run make build PY="$PY"
run make test PY="$PY"
run make lint PY="$PY"
beat

act "The control layer" \
    "Eight deterministic gates. No model is consulted in any of them: the decision" \
    "to allow or block is arithmetic over policy that lives in policy/ as YAML —" \
    "the same tables governance signed off."
run make gates PY="$PY"
beat

act "The gates refuse" \
    "This is the act that matters. Each gate has the thing it protects deliberately" \
    "broken, and must go red. A gate verified only by passing is indistinguishable" \
    "from a gate that cannot fail."
run make negative PY="$PY"
beat

act "The supervisory question" \
    "Which production changes touched control SEC-API-01, which were agent-authored," \
    "at what autonomy tier, and who approved each one?" \
    "" \
    "Seconds, from the repository. The playbook calls answering this in minutes" \
    "rather than a week the highest-value output of the whole programme."
run "$PY" scripts/query_evidence.py --control SEC-API-01
beat

act "Stage 6 — detection with no model in it" \
    "Western Electric rules over a 30-day rolling baseline, unit-tested including" \
    "the drift case no simple threshold catches. A model that decides whether" \
    "something is anomalous is a control you cannot evidence."
run "$PY" -m pytest scripts/tests/test_detect_anomaly.py -q
run "$PY" scripts/detect_anomaly.py
beat

act "The configuration regression suite" \
    "A change to AGENTS.md, a skill, a gate or a model route is a change to the" \
    "agent's behaviour, and gets regression-tested like the code it produces."
run make eval PY="$PY"
beat

act "The Substitution Test" \
    "Appendix C, scored by inspecting the repository rather than by self-assessment." \
    "Nothing scores a mark for a document that merely claims a property."
run make substitution PY="$PY"
beat

act "Change the agent vendor" \
    "The question third-party risk asks first. Every vendor answers 'nothing'." \
    "Here it is executed: each runtime is selected in turn and the repository" \
    "re-scores itself. A score that moves is a portability debt, not a refactor."
run make swap PY="$PY"
beat

if [ "$LIVE" -eq 1 ]; then
  act "Live — the pipeline on GitHub" \
      "Everything above ran locally. This is the same repository in CI."
  if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
    REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null || echo "")
    if [ -n "$REPO" ]; then
      say "Workflow runs on $REPO:"
      gh run list -R "$REPO" -L 8 2>/dev/null || true
      echo
      say "Tasks handed to the agent — assigned, not mentioned:"
      gh issue list -R "$REPO" -L 5 --json number,title,assignees \
        --jq '.[]|"  #\(.number) \(.title)\n      assignees: \([.assignees[].login]|join(", "))"' 2>/dev/null || true
    else
      say "No GitHub remote resolved; skipping the live act."
    fi
  else
    say "gh is not authenticated (\`gh auth login\`); skipping the live act."
  fi
  beat
fi

printf '\n%s%s──────────────────────────────────────────────────────────────%s\n' "$ORANGE" "$B" "$R"
if [ "$FAILED" -eq 0 ]; then
  printf '%s%s  Every act passed.%s\n\n' "$GREEN" "$B" "$R"
  cat <<'CLOSING'
  What was demonstrated, and what each part costs to move:

    the gates        arithmetic over YAML you wrote          yours
    the skills       portable markdown, named policy owner   yours
    the chain        commits in your repository              yours
    the evidence     emitted as controls execute             yours
    the agent        one line in .agent/runtimes.yaml        replaceable

  The agent drafted, proposed and reviewed. It decided nothing.

CLOSING
else
  printf '%s%s  An act failed. Fix it before showing this to anyone.%s\n\n' "$ORANGE" "$B" "$R"
fi
exit "$FAILED"

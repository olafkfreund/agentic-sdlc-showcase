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

# PY may be a path (.venv/bin/python) or a bare name (`python`, inside nix develop).
# `[ -x ]` only answers the first, so ask both and fall back once.
PY="${PY:-.venv/bin/python}"
command -v "$PY" >/dev/null 2>&1 || [ -x "$PY" ] || PY=python3

# Staging (colours, act/say/run/beat) is shared with pipeline_demo.sh.
DEMO_KIND="Act"
# shellcheck source=scripts/demo/lib.sh
. "$(dirname "$0")/lib.sh"

LIVE=0
for arg in "$@"; do
  case "$arg" in
    --fast) PAUSE=0 ;;
    --live) LIVE=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

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

closing "Every act passed."
if [ "$FAILED" -eq 0 ]; then
  cat <<'CLOSING'
  What was demonstrated, and what each part costs to move:

    the gates        arithmetic over YAML you wrote          yours
    the skills       portable markdown, named policy owner   yours
    the chain        commits in your repository              yours
    the evidence     emitted as controls execute             yours
    the agent        one line in .agent/runtimes.yaml        replaceable

  The agent drafted, proposed and reviewed. It decided nothing.

CLOSING
fi
exit "$FAILED"

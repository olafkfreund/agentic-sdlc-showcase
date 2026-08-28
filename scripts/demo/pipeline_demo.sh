#!/usr/bin/env bash
# The pipeline half of the demo: the same repository, running in CI.
#
# `run_demo.sh` proves the control layer on a laptop. This proves it in the place it
# actually has to hold — GitHub Actions, on a real change, with the gates reporting as
# required status checks. It watches live rather than reading a previous run, for the
# same reason nothing else here is replayed.
#
#   just pipeline           narrated, watches a live Stage 6 run
#   just pipeline --fast    no pauses, for a recording
#   just pipeline --observe don't trigger anything; narrate what already ran
#
# Read-only unless it triggers, and it only triggers Stage 6 — a detector against a
# fixture, which opens an issue and a branch and touches nothing else.
set -uo pipefail
cd "$(dirname "$0")/../.."

PAUSE=1
OBSERVE=0
for arg in "$@"; do
  case "$arg" in
    --fast) PAUSE=0 ;;
    --observe) OBSERVE=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

if [ -t 1 ]; then
  B=$'\e[1m'; DIM=$'\e[2m'; ORANGE=$'\e[38;5;208m'; GREEN=$'\e[38;5;142m'; RED=$'\e[38;5;167m'; R=$'\e[0m'
else
  B=""; DIM=""; ORANGE=""; GREEN=""; RED=""; R=""
fi

FAILED=0
ACT=0

act() {
  ACT=$((ACT + 1))
  printf '\n%s%s──────────────────────────────────────────────────────────────%s\n' "$ORANGE" "$B" "$R"
  printf '%s%s  Pipeline %d · %s%s\n' "$ORANGE" "$B" "$ACT" "$1" "$R"
  printf '%s%s──────────────────────────────────────────────────────────────%s\n\n' "$ORANGE" "$B" "$R"
  shift
  for line in "$@"; do printf '  %s%s%s\n' "$DIM" "$line" "$R"; done
  [ $# -gt 0 ] && echo
}

say() { printf '  %s%s%s\n\n' "$DIM" "$1" "$R"; }

# The terminal is the artifact here, so what is printed is what the viewer will read.
# `bash -c` is plumbing for a pipeline the shell cannot express as an argv, and showing
# it teaches the viewer nothing — so the wrapper is stripped from the display and only
# from the display. What runs is unchanged.
show() {
  if [ "${1:-}" = "bash" ] && [ "${2:-}" = "-c" ]; then
    printf '  %s$ %s%s\n\n' "$B" "$3" "$R"
  else
    printf '  %s$ %s%s\n\n' "$B" "$*" "$R"
  fi
}

run() {
  show "$@"
  if "$@"; then return 0; fi
  printf '\n  %sPIPELINE %d FAILED: %s%s\n' "$RED" "$ACT" "$*" "$R"
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

command -v gh >/dev/null || { echo "gh is not installed" >&2; exit 2; }
gh auth status >/dev/null 2>&1 || { echo "gh is not authenticated: gh auth login" >&2; exit 2; }
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null) || REPO=""
[ -n "$REPO" ] || { echo "no GitHub remote resolved" >&2; exit 2; }

printf '\n%s%s  The same control layer, running in CI%s\n' "$B" "$GREEN" "$R"
say "$REPO — nothing below is read from a previous run."
beat

act "What guards the default branch" \
    "These are required status checks, not advisory ones. A pull request cannot" \
    "merge until each reports green. Three of the four are the deterministic gates."
run gh api "repos/$REPO/branches/main/protection/required_status_checks" \
  --jq '.contexts[] | "  required: \(.)"'
say "And the human requirement that sits alongside them:"
run gh api "repos/$REPO/branches/main/protection/required_pull_request_reviews" \
  --jq '"  code owner review:        \(.require_code_owner_reviews)
  approval invalidated by push: \(.require_last_push_approval)"'
beat

act "Every stage has a workflow, and every workflow has run" \
    "A workflow that has never executed is a claim, not a control. This is the" \
    "count per workflow, from the API rather than from a screenshot."
run bash -c "gh run list -R '$REPO' -L 100 --json name --jq '[.[].name]|group_by(.)|map(\"  \(.[0]): \(length) run(s)\")|.[]' | sort"
beat

if [ "$OBSERVE" -eq 0 ]; then
  act "Stage 6 — the loop closes, with no human in the invocation path" \
      "A deterministic detector runs Western Electric rules over a 30-day rolling" \
      "baseline. No model decides whether something is anomalous: a model that did" \
      "would be a control you could not evidence." \
      "" \
      "At 3 sigma the agent writes its finding as an intent.md and pushes a branch." \
      "It cannot open the pull request — this repository declines the setting that" \
      "would allow that, because it is one toggle covering both 'create' and" \
      "'approve'. So it falls back to a triage issue, and a human opens the PR."
  run gh workflow run 06-operate.yml -R "$REPO"
  say "Watching it live:"
  sleep 6
  RUN=$(gh run list -R "$REPO" -L 5 --json name,databaseId,status \
        --jq '[.[]|select(.name=="Stage 6 — Operate")][0].databaseId')
  if [ -n "${RUN:-}" ]; then
    show "gh run watch $RUN"
    gh run watch "$RUN" -R "$REPO" --interval 5 --exit-status || FAILED=1
    echo
    say "What each job decided:"
    run gh run view "$RUN" -R "$REPO" --json jobs --jq '.jobs[]|"  \(.conclusion//"-")  \(.name)"'
  else
    say "Could not resolve the run id; skipping the watch."
    FAILED=1
  fi
  beat
fi

act "What the detector produced" \
    "A branch and a triage issue. The agent has no route to the default branch at" \
    "any autonomy tier, so this is as far as it gets on its own."
run bash -c "gh api 'repos/$REPO/branches' --jq '.[]|\"  branch: \(.name)\"'"
run bash -c "gh issue list -R '$REPO' -L 5 --state all --json number,title,labels,assignees --jq '.[]|\"  #\(.number) \(.title)\n      labels: \([.labels[].name]|join(\", \"))\n      assignees: \([.assignees[].login]|join(\", \")//\"(none)\")\"'"
say "The autonomy tier travels on the label, so what the agent was permitted to do is recorded where the work is."
beat

act "The gates, as they reported on a real pull request" \
    "This is the merged Stage 6 change. Every gate ran on the diff, and the" \
    "code-owner rule refused, because CODEOWNERS names one identity and that" \
    "identity authored the pull request. Segregation of duties, structurally."
PR=$(gh pr list -R "$REPO" --state merged -L 1 --json number --jq '.[0].number' 2>/dev/null)
if [ -n "${PR:-}" ]; then
  run bash -c "gh pr checks '$PR' -R '$REPO' 2>/dev/null | awk -F'\t' '{printf \"  %-34s %s\n\", \$1, \$2}'"
  say "The merge is attributable, and the override was recorded on the PR rather than done quietly:"
  run gh pr view "$PR" -R "$REPO" --json mergedBy,mergedAt,title \
    --jq '"  \(.title)\n  merged by \(.mergedBy.login) at \(.mergedAt)"'
else
  say "No merged pull request yet; skipping."
fi
beat

act "The release is attested" \
    "Signed in-toto provenance from your own CI, plus the gate results travelling" \
    "with the artifact — so 'which controls ran on the thing in production' is" \
    "answerable from the artifact alone, without asking a vendor for a report."
run bash -c "gh run list -R '$REPO' -L 4 --workflow=05-release.yml --json conclusion,displayTitle,createdAt --jq '.[]|\"  \(.conclusion//\"pending\")  \(.createdAt[0:16])  \(.displayTitle[0:52])\"'"
say "Production is a GitHub environment with a required reviewer — the gate is configuration, not a paragraph in a runbook:"
run bash -c "gh api 'repos/$REPO/environments' --jq '.environments[]|\"  \(.name): \([.protection_rules[].type]|join(\", \"))\"'"
beat

printf '\n%s%s──────────────────────────────────────────────────────────────%s\n' "$ORANGE" "$B" "$R"
if [ "$FAILED" -eq 0 ]; then
  printf '%s%s  The control layer holds in CI, not just on a laptop.%s\n\n' "$GREEN" "$B" "$R"
  cat <<'CLOSING'
  A detector with no model in it raised a finding with no human in the invocation
  path. The agent wrote it up and could go no further. Every gate ran on the diff.
  The human requirement refused, and the override was recorded in the open.

  None of that depended on which agent vendor was selected.

CLOSING
else
  printf '%s%s  A pipeline act failed. Fix it before showing this to anyone.%s\n\n' "$RED" "$B" "$R"
fi
exit "$FAILED"

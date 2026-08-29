# Shared prelude for the demo scripts. Sourced, never executed.
#
# `run_demo.sh` proves the control layer on a laptop; `pipeline_demo.sh` proves it in CI.
# They are different demonstrations with identical staging, and the staging had drifted
# into two copies — 47 identical lines, including the one function (`beat`) most likely to
# be edited in one file and forgotten in the other.
#
# Callers set DEMO_KIND to the word that labels an act ("Act", "Pipeline") before sourcing.

# Colour only when a human is watching; a redirected log or a cast gets clean text.
if [ -t 1 ]; then
  B=$'\e[1m'; DIM=$'\e[2m'; ORANGE=$'\e[38;5;208m'; GREEN=$'\e[38;5;142m'; RED=$'\e[38;5;167m'; R=$'\e[0m'
else
  B=""; DIM=""; ORANGE=""; GREEN=""; RED=""; R=""
fi

DEMO_KIND="${DEMO_KIND:-Act}"
PAUSE=1
FAILED=0
ACT=0
RULE="──────────────────────────────────────────────────────────────"

# act <title> [narration lines...]
act() {
  ACT=$((ACT + 1))
  printf '\n%s%s%s%s\n' "$ORANGE" "$B" "$RULE" "$R"
  printf '%s%s  %s %d · %s%s\n' "$ORANGE" "$B" "$DEMO_KIND" "$ACT" "$1" "$R"
  printf '%s%s%s%s\n\n' "$ORANGE" "$B" "$RULE" "$R"
  shift
  for line in "$@"; do printf '  %s%s%s\n' "$DIM" "$line" "$R"; done
  [ $# -gt 0 ] && echo
  return 0
}

say() { printf '  %s%s%s\n\n' "$DIM" "$1" "$R"; }

# The terminal is the artifact in a recording, so what is printed is what the viewer
# reads. `bash -c` is plumbing for a pipeline the shell cannot express as an argv, and
# showing it teaches nothing — so the wrapper is stripped from the display and only from
# the display. What runs is unchanged.
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
  printf '\n  %s%s %d FAILED: %s%s\n' "$RED" "$DEMO_KIND" "$ACT" "$*" "$R"
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

# closing <success line> — prints the rule, then the verdict.
closing() {
  printf '\n%s%s%s%s\n' "$ORANGE" "$B" "$RULE" "$R"
  if [ "$FAILED" -eq 0 ]; then
    printf '%s%s  %s%s\n\n' "$GREEN" "$B" "$1" "$R"
  else
    printf '%s%s  An act failed. Fix it before showing this to anyone.%s\n\n' "$RED" "$B" "$R"
  fi
}

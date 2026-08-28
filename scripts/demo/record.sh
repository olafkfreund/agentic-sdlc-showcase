#!/usr/bin/env bash
# Record the demo as an asciicast, repeatably.
#
#   just record              both casts: the control layer, and the pipeline
#   just record local        just the local demo
#   just record pipeline     just the CI demo (triggers a Stage 6 run)
#   just record --gif        also render GIFs (large; git-ignored)
#
# asciinema records the real session. It does not replay a script into a simulated
# terminal, which matters here: a screencast of a reconstruction would be exactly the
# artefact this repository spends nine acts arguing against. Every frame is the run.
#
# The casts are asciicast v2 — plain text, one JSON array per line, so a diff shows
# what changed between recordings and a reviewer can read what was on screen without
# playing anything back.
set -uo pipefail
cd "$(dirname "$0")/../.."

OUT="site/assets/casts"
COLS=100
ROWS=34
IDLE=1.6          # cap dead air; a viewer should not watch pip think
GIF=0
WHAT="all"

for arg in "$@"; do
  case "$arg" in
    local | pipeline | all) WHAT="$arg" ;;
    --gif) GIF=1 ;;
    *) echo "usage: record.sh [local|pipeline|all] [--gif]" >&2; exit 2 ;;
  esac
done

command -v asciinema >/dev/null || { echo "asciinema not found — use \`nix develop\`" >&2; exit 2; }

mkdir -p "$OUT"

# Marker events give the player a chapter track, so a viewer can jump to "the gates
# refuse" without scrubbing. The demo scripts already print the narration; this makes
# it navigable. Derived from what was actually on screen, never from a list kept here —
# a hand-maintained chapter list would drift from the recording it describes.
mark() {
  python3 - "$1" <<'PY'
import json, pathlib, re, sys

cast = pathlib.Path(sys.argv[1])
lines = cast.read_text().splitlines()
if not lines:
    sys.exit(0)

header, events = lines[0], lines[1:]
# An act banner looks like "  Act 3 · The gates refuse" or "  Pipeline 2 · ...",
# possibly wrapped in colour escapes.
banner = re.compile(r"(?:Act|Pipeline)\s+(\d+)\s+·\s+([^\r\n\x1b]+)")

out, seen = [], set()
for line in events:
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        out.append(line)
        continue
    if len(event) >= 3 and event[1] == "o":
        found = banner.search(event[2])
        if found and found.group(1) not in seen:
            seen.add(found.group(1))
            label = found.group(2).strip()
            out.append(json.dumps([event[0], "m", label]))
    out.append(line)

cast.write_text("\n".join([header, *out]) + "\n")
print(f"  {len(seen)} chapter marker(s)")
PY
}

record() {
  local name="$1" title="$2" command="$3"
  local cast="$OUT/$name.cast"
  printf '\n  recording %s -> %s\n' "$name" "$cast"
  # --headless: no TTY needed, so this runs the same from a terminal or from CI.
  if asciinema rec "$cast" \
      --format asciicast-v2 \
      --headless \
      --window-size "${COLS}x${ROWS}" \
      --idle-time-limit "$IDLE" \
      --overwrite \
      --title "$title" \
      --command "$command"; then
    :
  else
    printf '  the recorded session exited non-zero — the cast is kept so you can see why\n'
  fi
  mark "$cast"
  printf '  %s  (%s, %ss)\n' "$cast" \
    "$(du -h "$cast" | cut -f1)" \
    "$(python3 -c "
import json,sys
last=0.0
for l in open('$cast').read().splitlines()[1:]:
    try: last=json.loads(l)[0]
    except Exception: pass
print(round(last))
")"
}

gif() {
  [ "$GIF" -eq 1 ] || return 0
  command -v agg >/dev/null || { echo "  agg not found; skipping GIF" >&2; return 0; }
  local cast="$OUT/$1.cast"
  printf '  rendering %s.gif\n' "$1"
  agg --theme 1d2021,ebdbb2,282828,fb4934,b8bb26,fabd2f,83a598,d3869b,8ec07c,a89984,928374,fb4934,b8bb26,fabd2f,83a598,d3869b,8ec07c,ebdbb2 \
      --font-size 15 --speed 1.3 --idle-time-limit "$IDLE" \
      "$cast" "$OUT/$1.gif" 2>&1 | tail -2
}

# ---------------------------------------------------------------------------------

printf '\n  Recording the demo — %s\n' "$WHAT"

if [ "$WHAT" = "local" ] || [ "$WHAT" = "all" ]; then
  # The negative tests edit files and refuse to run on a dirty tree, so a recording
  # of a dirty tree would be a recording of act 3 declining to happen.
  if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "  working tree is dirty; commit or stash first (act 3 edits files)" >&2
    exit 2
  fi
  record "control-layer" \
    "Agentic SDLC — the control layer, in nine acts" \
    "bash scripts/demo/run_demo.sh --fast"
  gif "control-layer"
fi

if [ "$WHAT" = "pipeline" ] || [ "$WHAT" = "all" ]; then
  if gh auth status >/dev/null 2>&1; then
    record "pipeline" \
      "Agentic SDLC — the same control layer, running in CI" \
      "bash scripts/demo/pipeline_demo.sh --fast"
    gif "pipeline"
  else
    echo "  gh is not authenticated (gh auth login); skipping the pipeline cast" >&2
  fi
fi

printf '\n  Play locally:   asciinema play %s/<name>.cast\n' "$OUT"
printf '  On the site:    site/screencast.md embeds both\n\n'

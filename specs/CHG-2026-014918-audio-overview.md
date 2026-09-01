---
change_id: CHG-2026-014918
risk_class: R2
autonomy_tier: A2
controls: [TRC-01, CHG-04]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---

# Spec: a listen page, and a file sized for the web

## Requirements

### R1 — Encode for speech, once, deliberately

The source is AAC **stereo, 44.1 kHz, 257 kbps, 26m40s, 50 MB** — music-grade bitrate for a
two-person spoken-word conversation. It ships as **mono, 64 kbps, `+faststart`**: about
13 MB, no audible loss on speech, and the moov atom at the front so the browser streams
progressively rather than buffering the whole file before it plays.

The original is left untouched on disk and is not committed. Committing both would put 63 MB
in history to serve 13.

This is not a tidiness argument. Git history is append-only in practice: the difference
between 13 MB and 50 MB is paid by every clone, every CI checkout and every Pages build, for
the life of the repository, and it cannot be taken back later without rewriting history.

### R2 — A page, not a download

`/listen/` carries a native `<audio controls>` element with `preload="metadata"`, so a
visitor who does not press play transfers a few kilobytes rather than 13 MB. No player
library: the browser's own control is accessible, keyboard-navigable, remembers position
within the session, and adds no third-party script to a page that argues about supply chain.

### R3 — Say what it is

The page states plainly that the narration is AI-generated from the playbook by Google
NotebookLM, that the two voices are synthetic, and that the playbook is the source of truth
where the two differ. A synthetic conversation presented as commentary is exactly the
artefact that reads as authority while being a performance — the objection this repository
already records against `vhs` in `CHG-2026-014908`, and it applies to its own materials
or it means nothing.

### R4 — Findable

Navigation entry, a home-page pointer, and a README line. An asset nobody can find is not
published.

### R5 — Honest about what it will not do

The page says audio stops when you navigate, because this is a static multi-page site. A
visitor who presses play and clicks a link should have been told.

## Policy conflicts

None. No control, gate, risk class or frozen path is affected. `site/**` is claimed by the
plan so TRC-01 is satisfied; `policy/` is untouched, so this stays R2.

## Verification

- `make build test lint gates`.
- `ffprobe` on the shipped file: mono, ~64 kbps, duration matching the source.
- The published page returns 200 and the audio URL returns 200 with an audio content type
  and a `206` range response, which is what progressive playback depends on.

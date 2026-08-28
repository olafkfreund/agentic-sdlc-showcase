---
change_id: CHG-2026-014908
risk_class: R2
autonomy_tier: A2
controls: [TPR-05, TRC-01, CHG-04]
data_classification: public
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-balanced
supersedes: null
---

# Spec: a recorded demonstration that is the run, not a reconstruction

## Requirements

### R1 — asciinema, and deliberately not a scripted terminal renderer

Three tools were available: `asciinema`, `vhs` and `ttyd`.

`vhs` is the better-looking option. It takes a `.tape` file, types the commands into a
simulated terminal at a controlled pace, and produces a polished GIF. It is also, for
this repository specifically, **the wrong tool**: what it produces is a reconstruction of
a session that never happened. A recording of a simulated terminal is exactly the artefact
that reads as evidence while being a performance — the failure mode named in `REVIEW.md`,
in the gates, in the Substitution Test, and now in the screencast tooling.

`asciinema` records the real session: the process runs, and what it wrote to the terminal
is what lands in the cast. If a gate fails during a recording, the recording shows it.

The cast is **asciicast v2** — one JSON array per line, plain text. A reviewer can diff two
recordings and read what was on screen without playing anything.

### R2 — Both halves, and the CI half is live

| Cast | Script | Shows |
|---|---|---|
| `control-layer` | `run_demo.sh --fast` | Nine acts: the loop, the gates, twelve refusals, the supervisory question, detection, evals, the Substitution Test, the vendor swap |
| `pipeline` | `pipeline_demo.sh --fast` | Branch protection as configuration, every workflow's run count, a live Stage 6 run watched to completion, what the detector produced, the gates on a merged PR, the attested release |

The pipeline script triggers Stage 6 and watches it with `gh run watch`. It reads the run
that is happening, not one that happened. `--observe` narrates existing state without
triggering, for a rehearsal or a repeat within the same hour.

### R3 — Narration is on screen, and navigable

Both scripts already print, before each act, what is about to happen and why — that text
is in the terminal, so it is in the cast, so it is in the recording. No caption track, and
nothing that can drift from what it describes.

`record.sh` then post-processes the cast to insert asciicast **marker events** at each act
boundary, giving the player a chapter track. The labels are **derived from the banners the
run actually printed**, by scanning the recorded output — never from a list kept in the
recorder. A hand-maintained chapter list is a second description of the demo, and it would
drift from the first.

### R4 — Unattended, and honest about failure

`asciinema rec --headless` needs no TTY, so recording runs identically from a terminal or
from CI. Where the recorded session exits non-zero the cast is **kept, not discarded**, and
the script says so: the recording of a failure is the most useful recording there is, and
deleting it would be the tooling lying on the demo's behalf.

`--idle-time-limit` caps dead air so a viewer does not watch `pip` think.

### R5 — Playable on the site, readable as text

`site/screencast.md` embeds both casts with `asciinema-player` from a CDN. The `.cast`
files are committed, because they are the artifact; GIFs are rendered on demand by `agg`
and git-ignored, because they are a lossy convenience an order of magnitude larger.

### R6 — The toolchain is pinned

`asciinema` and `asciinema-agg` are declared in `flake.nix` and `devenv.nix`, alongside
everything else the demo needs. A recording tool that has to be installed by hand is the
same reproducibility gap `CHG-2026-014907` closed for the demo itself.

## Policy conflicts

**None identified.** Stated explicitly rather than omitted.

Considered and dismissed: the recordings show real change ids, real run ids and real
account names. They are this repository's own synthetic pipeline against a synthetic
payments service, already labelled as demo output in the README, the site footer and the
evidence bundle. `data_classification: public` is therefore correct rather than convenient.

## Verification

| Requirement | Verified by |
|---|---|
| R1 | The cast is asciicast v2 and diffs as text; `asciinema play` reproduces the session |
| R2 | Two casts exist; the pipeline cast contains a Stage 6 run watched to completion |
| R3 | Marker count reported by `record.sh` matches the act count in the script |
| R4 | `--headless` records with no TTY; a deliberately failed act leaves a kept cast |
| R5 | The site page plays both; `.cast` committed, `.gif` git-ignored |
| R6 | `nix flake check`; `asciinema` resolves inside `nix develop` |

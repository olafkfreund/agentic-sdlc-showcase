---
change_id: CHG-2026-014920
risk_class: R1
autonomy_tier: A2
controls: [TRC-01, CHG-04]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---

# Spec: one asset, named provenance, named gap

## Requirements

### R1 — One file, encoded once

The source is a 2752×1536 PNG at **5.8 MB**. It ships as a single **WebP at quality 80,
430 KB** — the same pixel dimensions, a 93% reduction, and verified legible at the densest
text in the image rather than assumed to be.

One file, not a responsive set: at 430 KB the full-resolution asset is smaller than most
hero images, so it serves both the inline render and the click-through. A second downscaled
copy would add bytes to history to save bytes that are not being spent.

`loading="lazy"` and explicit `width`/`height` so the browser reserves the space and the
page does not reflow when it arrives.

The original stays on disk beside the repository and is not committed, as under
CHG-2026-014918.

### R2 — Placed first, and framed

It goes above the screencast on the front page. The recording is the better artefact for
someone who already understands the argument; the graphic is for someone who does not yet.

### R3 — Alt text that carries the content

Not "infographic". The alt text describes the actual argument — the crossing-out of human
review, the chain into git, the Substitution Test question, the J-curve, the matrix — because
a screen-reader user should get the argument, not a label saying an argument exists.

### R4 — Provenance, and the three-versus-five gap, in the caption

The caption states it is AI-generated with NotebookLM from the playbook, and states plainly
that it maps three planes where §5 has five, naming the two that are missing. Same standard
applied to the audio under CHG-2026-014918 and to the rejection of `vhs` under
CHG-2026-014908.

## Policy conflicts

None. Presentation only. R1: nothing outside `site/` changes and no path floor applies.

## Verification

- `identify` on the shipped asset: 2752×1536, ~430 KB, WebP.
- `make build test lint gates`.
- Live: front page 200, asset 200 with an image content type.

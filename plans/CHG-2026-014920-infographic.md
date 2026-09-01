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

# Plan: encode, place, caption

## Files

- `site/**`

## Sequence

1. Encode WebP q80 at native size into `site/assets/img/`; move the PNG out of the tree.
   → verify: `identify` reports 2752×1536; TRC-01 stops refusing the stray PNG.
2. Read the image and write alt text from what it actually shows.
   → verify: the three-plane discrepancy was found this way, not assumed.
3. Add the figure to `site/index.md` above the screencast, with the caption from R4.
4. Style the figure: neutral surround so a cream image is not a hole in a dark page.
5. `make build test lint gates`; push; check the live URLs.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Publishing "three planes" unremarked, contradicting §5 | **certain if unread** | The image was read before it was placed. The caption names the gap and the two missing planes |
| 5.8 MB committed by reflex | high — it was sitting in the root | Encode first, commit the derivative, never `git add` the source |
| WebP artefacts on hand-drawn text | medium | Checked by cropping the densest text region out of the encoded file and looking at it |
| A cream image reads as a hole in a dark page | medium | Neutral border and ground; revisited under the light-theme change |
| Alt text that says nothing | medium | Describes the argument, not the medium |

## Rejected

- **Committing the 5.8 MB PNG.** Thirteen times the bytes, permanently, for no visible gain.
- **A responsive srcset.** The full-resolution asset is already 430 KB; extra copies would
  cost history to save nothing.
- **Editing the image to say five planes.** It is a generated artefact with a stated
  provenance. Retouching it to agree with the source makes the provenance false.
- **Not publishing it because of the error.** The graphic is good and the omission is
  nameable. Naming it is worth more than the graphic alone.

## Tests

`make build test lint gates`; `identify`; live 200s.

## Rollback

Revert. The asset stays in history, which is why R1 is decided once, carefully.

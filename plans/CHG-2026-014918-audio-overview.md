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

# Plan: encode, publish, link

## Approach

One page, one native element, no library. The only decision with consequences is the
encoding, because it is permanent.

## Files

- `site/**`
- `README.md`

## Sequence

1. Encode mono 64k with `+faststart` into `site/assets/audio/`. → verify: `ffprobe`
   reports 1 channel, ~64 kbps, unchanged duration.
2. Write `site/listen.md` with the player, the provenance note and the navigation caveat.
3. Link it: `_config.yml` nav, a home-page pointer, a README line.
4. `make build test lint gates`. → verify: green, TRC-01 satisfied by `site/**`.
5. Push, then request the live URLs. → verify: page 200; audio 200 with an audio
   content-type and range support.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| 50 MB committed by reflex and unremovable | **high** — the file was already sitting in the root | Encode first, commit the derivative, never `git add` the original |
| Git LFS breaks playback on Pages | certain if used | Not used. Pages does not resolve LFS objects |
| 13 MB downloaded by every visitor | high | `preload="metadata"` — bytes move only when play is pressed |
| Synthetic narration read as authored analysis | medium | Stated on the page, in the same terms the repository already applies to simulated terminals |
| A visitor navigates and the audio stops | certain | Said on the page rather than discovered |

## Rejected

- **Committing the 50 MB original.** Four times the bytes, permanently, for no audible gain
  on speech.
- **Git LFS.** Pages serves the pointer, not the audio.
- **An external host.** A dependency, an account and a link that rots, for one file the site
  can serve itself.
- **A JavaScript player.** The native element is accessible and adds no third-party script to
  a site whose playbook argues about supply chain.
- **A generated transcript.** Wanted, but unverified machine transcription published beside
  the audio is a second source of truth that disagrees with the first. Its own change.

## Tests

- `make build test lint gates`
- `ffprobe` on the shipped asset
- Live: page and asset both 200, asset supports range requests

## Rollback

Delete the page, the nav entry and the links. The asset stays in history regardless, which is
the reason R1 is decided carefully rather than quickly.

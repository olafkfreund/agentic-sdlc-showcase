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

# Plan: record the run, do not stage it

## Approach

The local demo is already scripted, narrated and exit-coded, so recording it is a wrapper
rather than a rewrite. The genuinely new work is the CI half — `pipeline_demo.sh` — which
had no equivalent, and which is where the claims that matter most to a sceptical audience
actually live.

Choose the recorder for correctness rather than polish, and say why in the spec: a
simulated terminal would look better and would make the demonstration the exact artefact
this repository argues against.

## Files

- `scripts/demo/record.sh`
- `scripts/demo/pipeline_demo.sh`
- `site/**`
- `flake.nix`
- `devenv.nix`
- `justfile`
- `.gitignore`
- `README.md`

## Sequence

1. `pipeline_demo.sh`, six acts against the live API, with `--observe` for a dry run.
   → verify: `just pipeline-observe` completes without triggering anything.
2. `asciinema` and `asciinema-agg` into the flake and devenv. → verify: `nix flake check`,
   and both resolve inside `nix develop`.
3. `record.sh`: headless capture, idle cap, fixed window, cast kept on failure.
   → verify: a cast is produced and `asciinema play` reproduces the session.
4. Marker post-processing derived from the recorded banners. → verify: marker count
   equals act count, and the labels match what was printed.
5. `just record` / `record local` / `record pipeline` / `--gif` / `play`.
   → verify: `just --list` reads as instructions.
6. `site/screencast.md` embedding both casts. → verify: the page plays them.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| The recording becomes a performance rather than a record | **high** — it is what recording tools are for | asciinema captures the real session; a failing act is recorded and the cast kept |
| A chapter list drifts from the demo it labels | high, over time | Markers are derived by scanning the recorded output, never hand-maintained |
| The recording rots while the demo keeps working | medium | Both scripts are exit-coded, so `just record` fails loudly rather than capturing a broken run silently |
| GIFs bloat the repository | medium | `.cast` is committed and is text; GIFs are rendered on demand and git-ignored |
| Recording the pipeline mutates the repository | medium | Only Stage 6 is triggered; it acts on a fixture and has no route to the default branch. `--observe` triggers nothing |
| A cast leaks a token in terminal output | low, high impact | Nothing in either script prints a secret; `gh` masks its own, and casts are reviewed as text before commit |

## Rejected

- **`vhs`.** Better-looking, and it types commands into a simulated terminal. The result
  is a reconstruction of a session that never happened, which is the artefact this
  repository exists to argue against. The reason is recorded in the spec so the decision
  survives the next person who notices the GIF would look nicer.
- **Editing takes together.** A spliced recording is a claim about a run that did not
  occur. If a take is wrong, fix the thing and record again.
- **Recording the GitHub web UI.** It is a rendering of the API, and the API is what the
  controls act on. The terminal shows the same facts and diffs as text.
- **Committing the GIFs.** An order of magnitude larger than the casts, and lossy.

## Tests

- `just pipeline-observe` — the CI narration, triggering nothing
- `just record local` — produces a cast with markers
- `asciinema play site/assets/casts/control-layer.cast` — reproduces the session
- `nix flake check` — the recorder is pinned

## Rollback

Delete the casts and the two scripts. Nothing depends on them: the demo, the gates and the
workflows are untouched by this change.

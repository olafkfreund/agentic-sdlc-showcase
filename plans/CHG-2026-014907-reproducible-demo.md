---
change_id: CHG-2026-014907
risk_class: R2
autonomy_tier: A2
controls: [TPR-05, TRC-01, CHG-04]
data_classification: public
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-balanced
supersedes: null
---

# Plan: pin the environment, script the demonstration

## Approach

Wrap, do not restate. The `Makefile` already defines the loop and the gates, and it is
what CI and `AGENTS.md` both point at; the justfile calls it. The demo script sequences
those same commands and narrates them.

The only genuinely new artefact is the ordering and the self-check — that the demo knows
when it has failed. That is what makes it a test rather than a performance, and it is why
this change was worth making rather than writing a runbook.

## Files

- `flake.nix`
- `flake.lock`
- `devenv.nix`
- `justfile`
- `.envrc`
- `scripts/demo/run_demo.sh`
- `README.md`

## Sequence

1. `flake.nix` with the pinned toolchain. → verify: `nix flake check` passes.
2. `devenv.nix` declaring the same set, deferring to the flake. → verify: it names the
   same tools and the same Python.
3. `justfile` delegating every loop recipe to `make`. → verify: `just --list` is
   self-explanatory; no `make` command is restated.
4. `scripts/demo/run_demo.sh`, nine acts, narrated, exit-coded. → verify: `just demo-fast`
   exits zero on a healthy tree, non-zero with a deliberately broken act.
5. `.envrc` for direnv users. → verify: `direnv allow` yields the shell.
6. README pointing at the one command. → verify: the claim matches the recipe.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| The justfile and the Makefile drift into two definitions of "green" | **high** — the standard fate of a second task runner | Every loop and gate recipe delegates to `make`; the justfile adds only what make is bad at |
| The demo rots silently between engagements | high | It exits non-zero on a failed act, so `just demo-fast` is a test and can run in CI |
| Nix becomes a precondition for running the repository | medium | Additive only; `python -m venv .venv && make` stays supported and is what CI uses |
| `make negative` refuses to run because the tree is dirty | medium, and it will happen mid-demo | The script surfaces the message rather than swallowing it; the fix is to commit, which is the correct instruction |
| The demo appears to pass because an act printed something plausible | medium | Each act's exit status is checked, not its output |

## Rejected

- **Replacing the Makefile with the justfile.** CI, `AGENTS.md` and the eval suite all
  reference `make`. Moving them buys tidiness and costs the property that the agent and
  CI run literally the same commands.
- **Recording the demo and replaying it.** Faster and reliable, and it would make the
  demonstration exactly the artefact this repository argues against.
- **Adding the demo as a gate.** It is a rehearsal tool. A gate that runs nine acts on
  every pull request buys nothing the individual gates do not already prove.

## Tests

- `just demo-fast` — the whole sequence, exit-coded
- `nix flake check` — the environment evaluates
- `just ci` — check, eval, substitution, negative in CI's order

## Rollback

Delete the four new files. Nothing depends on them: the Makefile, the gates and the
workflows are untouched by this change.

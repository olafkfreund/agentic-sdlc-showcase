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

# Spec: a pinned environment and one command that performs the demonstration

## Requirements

### R1 — `flake.nix` pins the toolchain

Python 3.12 with the service's dependencies, plus `just`, `make`, `git`, `gh`, `jq` and
ruby for previewing the site. `nix flake check` builds the shell, so a broken environment
is caught by CI rather than by a presenter.

`devenv.nix` declares the same toolchain for people who use devenv, and says in its own
header that `flake.nix` is canonical — a second environment definition that claims
equality is how the two come to disagree.

### R2 — `justfile` orchestrates; `Makefile` still defines

Every recipe that touches the loop or the gates calls `make`. The `Makefile` is what CI
runs and what `AGENTS.md` tells the agent to run, so restating those commands in a second
file would produce two definitions that drift, and the drift would surface on the day the
two disagreed about what "green" meant.

`just` adds what `make` is bad at: discoverability (`just` lists every recipe with its
purpose), arguments (`just evidence DP-11`), and orchestration of the demo itself.

### R3 — The demo is ordered, narrated and self-checking

`scripts/demo/run_demo.sh` runs nine acts in the order the argument needs:

| Act | Shows |
|---|---|
| 1 | The closed loop — the same commands the agent runs |
| 2 | Eight deterministic gates passing |
| 3 | **All twelve gates refusing.** The act that matters |
| 4 | The supervisory question answered from the repository |
| 5 | Stage 6 detection, unit-tested, with no model in it |
| 6 | The configuration regression suite |
| 7 | The Substitution Test, scored from the tree |
| 8 | The agent vendor changed four ways, re-scored under each |
| 9 | *(opt-in)* the live pipeline on GitHub |

Each act prints the command before running it, so the audience sees what produced the
output. A failing act sets a flag and the script exits non-zero — **the demo is testable,
which is the property that stops it rotting between engagements.**

`--fast` removes the pauses for recording or CI; `--live` adds the GitHub act and degrades
to a printed note when `gh` is not authenticated.

### R4 — Nothing is staged

Every number the demo prints is computed during the run, against this repository. No
fixture of a previous run, no recorded output, no mock. A demo that replays a good day is
the same artefact as a control that reads as operating while it is not.

## Policy conflicts

**None identified.** Stated explicitly rather than omitted: an absent section is
indistinguishable from an unperformed check.

Considered: adding Nix as a repository dependency would narrow who can run this. It is
therefore additive only — `python -m venv .venv && make` remains supported and is what CI
uses, so the pinned environment is a convenience for the presenter rather than a
precondition for the argument.

## Verification

| Requirement | Verified by |
|---|---|
| R1 | `nix flake check` evaluates the shell and the check package |
| R2 | Every loop recipe in the justfile delegates to `make`; no command is restated |
| R3 | `just demo-fast` exits zero on a healthy tree and non-zero when an act fails |
| R4 | The demo reads no fixture except `ops/fixtures/`, which is the detector's input |

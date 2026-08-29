---
change_id: CHG-2026-014911
risk_class: R2
autonomy_tier: A2
controls: [TRC-01, CHG-04, TPR-05]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-balanced
supersedes: null
---

# Spec: nine cuts, two of them withdrawn on inspection

## Requirements

### R1 — One `scripts/demo/lib.sh`, sourced by both demos

Colours, `act`, `say`, `show`, `run`, `beat` and a new `closing` move to a sourced file.
Callers set `DEMO_KIND` ("Act", "Pipeline") before sourcing, which is the only thing that
differed between the two copies.

### R2 — One `site/_includes/player.html`

Pulled in by the layout where a page's front matter sets `casts: true`, rather than pasted
into every page that plays a recording.

### R3 — Nothing declared that nothing reads

| Cut | Read by |
|---|---|
| `contract:` block in `runtimes.yaml` (18 lines) | no code — moved into the file's header comment, where it was already half-documented |
| `context_file:` × 4 runtimes | nothing; the prompts name `AGENTS.md` directly |
| `agent-task` `route` output | no workflow |
| `theme_name` in `_config.yml` | no layout |

### R4 — Only recipes with no caller are removed

`test`, `lint`, `gates` and `demo-live` had zero external references. Removed, with a
comment at `check` saying where they went so their absence reads as a decision.

**Two findings were withdrawn.** The audit proposed also cutting `eval` and `negative` as
bare aliases. They are referenced by `CONTRIBUTING.md`, the pull request template and both
shell hooks; and `demo-fast` is named in the verification sections of two chain artifacts,
which are historical records. Cutting them would have broken live instructions to improve a
line count.

That correction is worth recording: **an audit that measures duplication without checking
callers produces confident wrong advice**, which is the same defect as a gate that passes
without running.

## Policy conflicts

**None identified.** Stated explicitly rather than omitted.

## Verification

| Requirement | Verified by |
|---|---|
| R1 | Both demos run; `Act N FAILED` / `Pipeline N FAILED` label correctly via `DEMO_KIND` |
| R2 | Both pages still play their casts in a browser |
| R3 | Stage 0's context-plane check passes; `make swap` still reports a one-line diff |
| R4 | `just --list` reads correctly; `just ci` resolves to the same four `make` calls |
| all | `make build test lint gates`, `make negative`, `make eval`, `make substitution` unchanged |

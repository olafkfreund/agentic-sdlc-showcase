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

# Plan: check the callers first, then cut

## Approach

Grep for external callers before removing anything. That step is what turned nine cuts into
seven and is the only interesting part of the work.

## Files

- `scripts/demo/**`
- `site/**`
- `justfile`
- `.agent/runtimes.yaml`
- `.github/actions/agent-task/**`

## Sequence

1. Grep every candidate for external references. → verify: two findings withdrawn.
2. Extract `scripts/demo/lib.sh`; both demos source it. → verify: both run, act labels correct.
3. Extract `site/_includes/player.html`; layout includes it on `page.casts`. → verify: both
   pages play in a browser.
4. Remove the unread config, the unconsumed output and the four uncalled recipes.
   → verify: Stage 0 context-plane check passes; `just ci` resolves.
5. Re-run everything. → verify: identical scores.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| A cut breaks a documented command | **high** — it nearly did, twice | Every candidate grepped for callers before removal; two withdrawn |
| The refactor changes demo output | medium | Both demos run before and after and compared |
| `lib.sh` is executed rather than sourced | low | Header says sourced, never executed; no shebang, not chmod +x |
| The player include is pulled onto every page | medium | Guarded on `page.casts`, set only where a cast exists |

## Rejected

- **Cutting `eval` and `negative`.** Referenced by CONTRIBUTING, the PR template and both
  shell hooks.
- **Cutting `demo-fast`.** Named in two chain artifacts' verification sections.
- **Merging the eight gate files.** `controls.yaml` maps objectives to gates by filename.
- **Deleting `devenv.nix`.** Duplicates the flake, and was explicitly asked for.

## Tests

- `make build test lint gates`, `make negative`, `make eval`, `make substitution`
- Both demo scripts, run directly
- `make swap` — still a one-line diff

## Rollback

Revert. The refactor is behaviour-preserving, so nothing downstream depends on it.

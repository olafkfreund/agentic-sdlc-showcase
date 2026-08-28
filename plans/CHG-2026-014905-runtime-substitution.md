---
change_id: CHG-2026-014905
risk_class: R3
autonomy_tier: A2
controls: [TPR-05, CHG-04, TRC-01, HUM-14]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---

# Plan: declare the runtime, adapt it once, prove it by switching

## Approach

Generalise rather than add. The repository already invoked the agent in exactly two
places, which is the only reason this change is small — so the work is to turn those two
places into one adapter driven by configuration, not to build a plugin system.

The proof comes last and is the actual deliverable: `make swap` switches through every
runtime and re-scores the repository under each. If the scores are identical the claim
holds; if one moves, the abstraction leaked and the script says so. Anything less is the
self-assessment the Substitution Test exists to replace.

## Files

- `.agent/runtimes.yaml`
- `.github/actions/agent-task/**`
- `.github/workflows/00-foundations.yml`
- `.github/workflows/02-design.yml`
- `.github/workflows/05-review.yml`
- `.github/workflows/06-operate.yml`
- `scripts/switch_runtime.py`
- `scripts/demo/swap/**`
- `Makefile`
- `site/**`

## Sequence

1. Declare the runtime plane in `.agent/runtimes.yaml`, including the contract every
   runtime is handed. → verify: parses; `selected` is a declared runtime.
2. Replace `assign-copilot` with `agent-task`, carrying both invocation shapes and
   resolving the route from the binding. → verify: an undeclared binding fails loudly.
3. Rewire Stages 2 and 6 to the adapter; strip the vendor mention from the task text.
   → verify: no workflow contains a declared runtime identifier.
4. Read the reviewer identity from the runtime in Stage 5, with an honest path for a
   runtime that has none. → verify: `reviewer: null` produces a warning, not a green check.
5. Add `switch_runtime.py` and the blast-radius report. → verify: the swap writes one
   file; the invariant inventory is clean.
6. Add `make swap` and the scoring loop. → verify: identical gates, evals and
   Substitution Test under all four runtimes, original selection restored.
7. Enforce it at Stage 0. → verify: the check fails when a vendor identifier is put back
   into a workflow.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| The abstraction fits only the shape it was built for | **high** — it was built against one vendor | Two invocation shapes from the start; the hosted shape is exercised by `make swap` even though it cannot run live here |
| A vendor identifier creeps back into a stage during a later change | high, over time | Stage 0 collects the identifiers from `runtimes.yaml` and fails the build on any of them appearing in a workflow |
| A runtime that reads its own instructions file forks the context plane | medium | Every runtime declares `context_file: AGENTS.md` and is prompted to read it; Substitution Test #1 fails if a second context file appears |
| A model name arrives via a runtime declaration | medium | `substitution_test.py` check 5 already scans every YAML in the tree, this file included |
| `make swap` reports a flattering number from an unrelated dirty tree | medium | The diff is scoped to the file the switch writes, and the invariant inventory is checked separately |
| The hosted runtimes appear to work when they cannot | **high, and the failure this repository is about** | Gated on `AI_GATEWAY_ENABLED`; the step writes a plain summary saying no agent took the task and emits a warning, and never reports success |

## Rejected

- **A thirteenth Substitution Test check.** Appendix C has twelve. Inventing one to score
  better is precisely the self-assessment the test replaces.
- **A plugin interface with a registry.** Four runtimes, two shapes, one `if:` each. An
  interface with one real implementation and three aspirational ones is worse than a
  conditional.
- **Committing a provider key so the other runtimes run live.** It would demonstrate the
  swap by breaking the constraint the swap exists to protect.
- **Resolving the autonomy conflict in the spec.** Named in the spec, left to its owners.

## Tests

- `make swap` — every runtime, every score, restored afterwards
- Stage 0 context-plane validation — the runtime plane, the bindings, the identifiers
- `make negative` — unchanged; the control layer does not depend on any runtime

## Rollback

Revert the commit. The adapter is additive over the two call sites it replaced, and the
runtime plane is one file; nothing downstream holds state.

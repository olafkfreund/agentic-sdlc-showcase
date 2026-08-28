---
change_id: CHG-2026-014880
risk_class: R3
autonomy_tier: A2
controls: [CHG-04, TRC-01, HUM-14, TPR-05, SEC-API-01, DP-11, FIN-02, FRZ-01, SOD-01]
data_classification: internal
originator: olaf.krasicki-freund@synechron.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---


# Plan: build the showcase

## Approach

Build the payload first so the gates have something real to act on, then the gates, then
the portability layer, then the workflows that run them. Prove each gate by breaking the
code it protects and watching it refuse — a gate verified only by passing is not verified.

The repository is built through its own chain: this plan claims every path, so
`check_plan_conformance.py` holds for the scaffolding exactly as it will for a feature.

## Files

- `AGENTS.md`
- `README.md`
- `REVIEW.md`
- `Makefile`
- `pyproject.toml`
- `.gitignore`
- `CODEOWNERS`
- `.github/**`
- `service/**`
- `scripts/**`
- `policy/**`
- `ops/**`
- `.agent/**`
- `docs/**`
- `evidence/.gitkeep`

## Sequence

1. Payload service and the closed loop. → verify: `make build test lint` green.
2. Policy YAML and the seven gates. → verify: each gate refuses a deliberately broken
   change and passes once reverted.
3. Skills, routes, MCP allowlist, OTel collector. → verify: Substitution Test rises.
4. Eval suite. → verify: 24 cases, `--mode static` at or above 90%.
5. Stage 6 detection and its unit tests. → verify: `pytest scripts/tests/` green,
   including the drift case that no threshold would catch.
6. Seeded artifact chains. → verify: `check_artifact_header.py` passes, chain complete.
7. Workflows. → verify: valid YAML, Substitution Test reaches 12/12.
8. Evidence query and the demo script. → verify: the §6.2 supervisory question answered
   from the repository in one command.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| A gate passes vacuously and nobody notices | **high** — the default failure mode of this kind of work | Every gate has a negative test in `scripts/demo/negative/`; the Substitution Test refuses to award a mark for a document that merely claims a property |
| Demo evidence is mistaken for real audit records | low, high impact | Labelled as demo output in the README, the query tool and the bundle |
| The org has no Copilot coding agent, so Stages 2/3/5 cannot run live | medium | Copilot is invoked in one step per stage; the gates and the chain are unaffected, and the fallback is an `@copilot` PR mention |
| The repository exempts itself from its own gates | medium | This plan; R4 in the spec |

## Rejected

- Building the gates before the service. Faster to start, and every gate would have been
  verified against a hypothetical rather than real code.
- Skipping the negative tests to save time. That is precisely the corner whose absence
  the whole document argues against.

## Tests

- `service/tests/` — the payload's own suite
- `scripts/tests/test_detect_anomaly.py` — the Stage 6 detector, including drift
- `scripts/tests/test_review_tally.py` — the severity arithmetic that gates a merge
- `scripts/demo/negative/` — one scripted branch per gate, each of which must go red

## Rollback

The repository is new; rollback is deletion. No downstream consumer exists yet.

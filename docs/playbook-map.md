# Playbook → repository map

Every executable claim in the Agentic SDLC Playbook v1.0, and where it runs here.
Sections with no row are narrative or commercial and have nothing to execute.

## §4 Design principles

| # | Principle | Where it is enforced |
|---|---|---|
| 1 | Artifacts over sessions | `intent/`, `specs/`, `plans/` — git is the timestamp authority |
| 2 | Open formats over vendor files | `AGENTS.md` is the source of truth; `.github/copilot-instructions.md` is a pointer, and `substitution_test.py::check_01` fails if it grows past 80 words |
| 3 | Enforcement lives outside the agent | `scripts/check_*.py` run in CI, not in the agent's context |
| 4 | No model in the gate | `scripts/gate.py` module docstring; `evals/cases/021` regression-tests it |
| 5 | Evidence as a by-product | `gate.report()` writes an evidence record every time a gate runs |
| 6 | Least privilege, tiered by environment | `policy/autonomy-matrix.yaml`, GitHub environments |
| 7 | Human judgement at the gates | `CODEOWNERS`, `production` environment reviewers, `REVIEW.md` |

## §5 Five planes

| Plane | Artifact |
|---|---|
| 5.1 Model access | `.agent/routes.yaml` |
| 5.2 Agent runtime | `.github/workflows/*` — Copilot in one step per stage |
| 5.3 Context | `AGENTS.md`, `.agent/skills/`, `.agent/mcp-allowlist.yaml` |
| 5.4 Control | `policy/`, `scripts/check_*.py`, `CODEOWNERS` |
| 5.5 Evidence | `evidence/`, `ops/otel-collector.yaml`, `actions/attest-build-provenance` |

## §6 The artifact chain

| Element | Here |
|---|---|
| 6.1 The chain | `intent/` → `specs/` → `plans/` → diff → PR → release; gaps rejected by `check_artifact_header.py` |
| 6.2 The header | `docs/artifact-header.md`; validated by `scripts/artifacts.py::validate` |
| 6.2 The query | `scripts/query_evidence.py` |
| 6.3 Systems of record | `itsm_record` in the header; `.agent/mcp-allowlist.yaml` allows the ServiceNow MCP server |

## §7 Stage plays

| Stage | Workflow | Gate | Evidence |
|---|---|---|---|
| 0 Foundations | `00-foundations.yml` | `substitution_test.py` | `evidence/substitution_test.json` |
| 1 Plan | `01-intent.yml` | `check_artifact_header.py` + required sections | git history |
| 2 Design | `02-design.yml` | `spec-author` skill; conflicts flagged, not resolved | the spec itself |
| 3 Build | `03-gates.yml` | `check_plan_conformance.py`, `check_frozen_paths.py`, `check_autonomy.py` | `evidence/*.json` |
| 4 Test | `04-test.yml` | `make build test lint`; eval pass rate on config changes | `evidence/evals.json` |
| 5 Deploy | `05-review.yml`, `05-release.yml` | `review_tally.py`; SoD; environment reviewers | attestations |
| 6 Operate | `06-operate.yml` | `detect_anomaly.py` (deterministic, unit-tested) | `evidence/anomaly_detection.json` |

## §8 Governance

| Section | Here |
|---|---|
| 8.1 Risk classes | `policy/risk-classes.yaml`, including `path_floors` so a change cannot self-declare its way past a gate |
| 8.2 Autonomy tiers | `policy/autonomy-matrix.yaml` |
| 8.3 The matrix | same file, enforced by `check_autonomy.py` |
| 8.4 Control mapping | `policy/controls.yaml` — every objective names its gate and its evidence |
| 8.5 Threats | prompt injection: `AGENTS.md` Trust section + evals 011/012. Supply chain: `.agent/mcp-allowlist.yaml`. Evidence integrity: append-only export in `ops/otel-collector.yaml` + eval 023 |

## §9 Measurement

Tier 2 metrics this repository actually emits:

| Metric | Source |
|---|---|
| Plan-to-diff conformance | `evidence/plan_conformance.json::conformance_rate` |
| Eval pass rate | `evidence/evals.json::pass_rate` |
| Agent-attributed changes | `query_evidence.py --agent-authored` |
| `AGENTS.md` coverage | `substitution_test.py::check_01` |

**Tier 3 — not measured, deliberately.** No lines of code, commits, PR count, tokens, or
"AI adoption percentage" anywhere in this repository. Every one is trivially gamed by an
agent, and optimising for them produces volume and review debt.

## Appendices

| | Here |
|---|---|
| A — `AGENTS.md` skeleton | `AGENTS.md`, filled for the payments service |
| B — `SKILL.md` skeleton | `.agent/skills/secure-api-review/`, with `scripts/check_endpoints.sh` as its paired gate |
| C — Substitution Test | `scripts/substitution_test.py`, run weekly by `00-foundations.yml` |

## Deliberate departures

| Playbook says | Here | Why |
|---|---|---|
| "policy-as-code in CI (OPA / Rego, Conftest)" | Python gates over version-controlled YAML | Rego *and* Python means two homes for one rule, and they drift. The control requirement is a deterministic enforcement point outside the agent, which this satisfies. Conftest is the swap-in for OPA estates — replacing the Python, not duplicating it. |
| A model access gateway | Declared in `.agent/routes.yaml`, not stood up | Out of scope for a reference repository. The eval runner's `--mode gateway` speaks the protocol and is wired but unexercised here. |
| Signed attestations to a compliance store | `actions/attest-build-provenance` to GitHub's own store | Same in-toto/SLSA form, no third party to onboard for a demo. |

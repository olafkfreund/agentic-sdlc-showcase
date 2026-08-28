# Agentic SDLC — runnable reference implementation

**→ [olafkfreund.github.io/agentic-sdlc-showcase](https://olafkfreund.github.io/agentic-sdlc-showcase/)**
— the stages, the gates, the Substitution Test and the artifact chain, published from
this tree by [`site/build_pages.py`](site/build_pages.py) so the page cannot drift from
the repository it describes.

A working implementation of the **[Agentic SDLC Playbook v1.0](docs/playbook-map.md)**:
seven stages, five planes, a portable artifact chain, an autonomy matrix, and the
Substitution Test — as code that runs, gates that refuse, and evidence that is a
by-product rather than a reconstruction.

**GitHub Copilot is the agent runtime here.** Deliberately. The playbook's argument is
that the operating model must survive a change of vendor, so the honest way to make that
case is to use a specific vendor's agent while keeping every asset in open formats. Copilot
is invoked in exactly one step per stage. Swapping it is an edit to those steps; the
context, the skills, the policy, the gates and the evidence do not move.

```
  Substitution Test    12/12  — portable, and re-scored under every agent vendor
  Deterministic gates  12/12  — each proven to refuse, not just to pass
  Evals                24/24  — configuration regression, non-interactive
```

> **Demo data.** The evidence records, attestations and change IDs here are produced by
> this repository's own pipeline against a synthetic payments service. They are not any
> institution's audit records, and nothing in this repository should be presented as one.

---

## Try it in two minutes

With Nix — the toolchain is pinned, so it behaves the same on a machine that has never
seen this repository:

```bash
nix develop          # or: devenv shell, or: direnv allow
just demo            # the whole thing, narrated, nine acts
```

Prefer to watch rather than run? Both halves are recorded, and the recordings are of
the real session: **[olafkfreund.github.io/agentic-sdlc-showcase/screencast/](https://olafkfreund.github.io/agentic-sdlc-showcase/screencast/)**.
`just record` reproduces them.

`just demo` exits non-zero if any act fails, which is what stops it rotting between
engagements: the demonstration is a test, not a performance. `just demo --fast` drops the
pauses; `just demo --live` adds the pipeline running on GitHub.

Without Nix, nothing is lost — this is what CI runs:

```bash
python -m venv .venv && .venv/bin/pip install -e '.[dev]'
make build test lint gates     # the closed loop plus the control layer
make substitution              # Appendix C, scored from the repository
make eval                      # 24 configuration regression cases
make negative                  # break each protected thing; watch every gate refuse
make swap                      # switch agent vendor 4 ways; re-score under each
```

`make negative` is the one that matters. A gate verified only by passing is
indistinguishable from a gate that cannot fail.

---

## The 30-minute walkthrough

### 1. The bottleneck has moved (§2)

Open [`intent/CHG-2026-014882-refund-endpoint.md`](intent/CHG-2026-014882-refund-endpoint.md)
→ [`specs/`](specs/) → [`plans/`](plans/). Three commits, three authors, three timestamps.
The chain of commits **is** the audit trail. No transcript, no chat window, no vendor's
session store.

### 2. Controls that describe reality (§6.2)

Every artifact opens with a machine-readable header. That is what makes this possible:

```bash
python scripts/query_evidence.py --control SEC-API-01
```

> *Which production changes touched control SEC-API-01, which were agent-authored, at
> what autonomy tier, and who approved each one?*

Seconds, from the repository. The playbook calls answering this in minutes rather than a
week "the single highest-value output of this whole programme".

### 3. The gate refuses (§5.4)

```bash
make negative
```

Twelve deliberate violations — a float on a monetary field, a personal field in an error
message, an unaudited `POST`, an edit to a frozen path, an R3 change claiming A3
autonomy, code with no plan claiming it. Every one refused, by code, with the control id
and the reason.

**No model in the gate** (principle 4). Models diagnose, propose, draft and review. The
decision to allow or block is arithmetic over policy that lives in
[`policy/`](policy/) as version-controlled YAML — the same tables governance signed off.

### 4. Policy applied while the spec is written (§Stage 2)

Open [`specs/CHG-2026-014901-fx-rounding.md`](specs/CHG-2026-014901-fx-rounding.md). Its
`## Policy conflicts` section names two standards that cannot both hold, their owners,
and the options with their trade-offs — and **does not resolve them**. The chain stops
there, at `autonomy_tier: A0`, awaiting the Group Financial Controller and the DPO.

That is the Stage 2 control point working, not failing. Finding this conflict during the
design pass instead of in a review three weeks later is most of the value of the stage.

### 5. The substitution (§Appendix C)

```bash
make substitution
```

Twelve checks, executed against the repository rather than self-assessed — nothing scores
a mark for a document that merely claims a property. The check for raw model names scans
every file in the tree, including the one you are least likely to check.

### 6. The vendor changes, and nothing else does (§5.2, Appendix C)

```bash
make swap
```

```
  runtime    gates     evals    subst    cost vs HEAD
  copilot    8/8       24/24    12/12    0+ 0-
  claude     8/8       24/24    12/12    1+ 1-
  gemini     8/8       24/24    12/12    1+ 1-
  codex      8/8       24/24    12/12    1+ 1-
```

The deterministic gates, the eval suite and the Substitution Test are re-run under each
runtime. A score that moves under a vendor change is a portability debt, not a refactor,
and the script exits non-zero if one does.

Two invocation shapes are supported, because they are genuinely different: an identity
**assigned** in the VCS (Copilot, no provider key) and a hosted **step** taking its
credential from the gateway (Claude, Gemini, Codex). Both live in
[`.github/actions/agent-task`](.github/actions/agent-task/action.yml), and Stage 0 fails
the build if any workflow wires a vendor identifier directly — without that check the
abstraction rots back into a hard-coded vendor within two quarters.

**No runtime names a model.** A vendor name is a fact about who you buy from; a model name
pinned in your repository is a migration you have not scheduled yet.

### 7. The loop closes (§Stage 6)

```bash
python scripts/detect_anomaly.py
```

Western Electric rules over a 30-day rolling baseline, unit-tested including the **drift**
case that no simple threshold catches. **No model in detection.** At 3σ,
[`06-operate.yml`](.github/workflows/06-operate.yml) has the agent write its diagnosis as
an `intent.md` — and from there it re-enters at Stage 1 like any other change, through
every gate, with a human triaging the queue.

---

## What is where

| Plane (§5) | Here | The point |
|---|---|---|
| Model access | [`.agent/routes.yaml`](.agent/routes.yaml) | Routes, never model names. No provider key outside the gateway. |
| Agent runtime | [`.agent/runtimes.yaml`](.agent/runtimes.yaml), [`.github/actions/agent-task/`](.github/actions/agent-task/action.yml) | Copilot, Claude, Gemini or Codex. `make swap RUNTIME=<name>` — one line. The most replaceable component, and proven so. |
| Context | [`AGENTS.md`](AGENTS.md), [`.agent/skills/`](.agent/skills/), [`.agent/mcp-allowlist.yaml`](.agent/mcp-allowlist.yaml) | `.github/copilot-instructions.md` is a five-line pointer, never a source of truth. |
| Control | [`policy/`](policy/), [`scripts/check_*.py`](scripts/), CODEOWNERS, environments | Advisory layer makes violations rare; the deterministic layer makes them impossible. |
| Evidence | [`evidence/`](evidence/), [`ops/otel-collector.yaml`](ops/otel-collector.yaml), attestations | Emitted as controls execute. Never reconstructed. |

The public site is [`site/`](site/), built by [`pages.yml`](.github/workflows/pages.yml)
with the Jekyll engine. The playbook and every artifact page are generated at build time
from the files on disk, through the same parser the gates use — so the site is not a
second source of truth.

| Stage | Workflow | Control point |
|---|---|---|
| 0 Foundations | [`00-foundations.yml`](.github/workflows/00-foundations.yml) | Substitution Test scored weekly; context plane validated |
| 1 Plan | [`01-intent.yml`](.github/workflows/01-intent.yml) | Product owner accepts; acceptance **is** the merge |
| 2 Design | [`02-design.yml`](.github/workflows/02-design.yml) | Named policy owners resolve flagged conflicts |
| 3 Build | [`03-gates.yml`](.github/workflows/03-gates.yml) | Plan-to-diff conformance; frozen paths; autonomy matrix |
| 4 Test | [`04-test.yml`](.github/workflows/04-test.yml) | Eval pass rate gates configuration changes |
| 5 Deploy | [`05-review.yml`](.github/workflows/05-review.yml), [`05-release.yml`](.github/workflows/05-release.yml) | Severity tally, not narrative; environment approval; author ≠ approver |
| 6 Operate | [`06-operate.yml`](.github/workflows/06-operate.yml) | Tier boundaries from version-controlled config; no production write access |

---

## Before you demo this

Two organisation settings shape what the audience sees — both documented in
[`docs/org-prerequisites.md`](docs/org-prerequisites.md):

- **The Copilot coding agent is invoked by assignment, not by a mention.** `@copilot` in
  an issue body renders and starts nothing. [`.github/actions/assign-copilot`](.github/actions/assign-copilot/action.yml)
  assigns the task and then re-reads the assignees to confirm it landed — and where the
  agent is unavailable it says so plainly instead of reporting a green check for a step
  that did nothing. The gates, the chain and the evidence are unaffected either way,
  which is the point worth making: the control layer depends on no agent.
- **"Allow Actions to create and approve pull requests" is deliberately off.** It is one
  toggle covering both verbs, and this repository will not trade segregation of duties
  for convenience. Stage 6 opens a triage issue with the branch instead, and the loop
  closes just the same.

## Adopting this

1. Replace the teams in [`CODEOWNERS`](CODEOWNERS) with real ones.
2. Point [`.agent/routes.yaml`](.agent/routes.yaml) at your gateway; revoke direct
   provider keys.
3. Rewrite [`policy/controls.yaml`](policy/controls.yaml) against your control library and
   your regulators.
4. Replace [`service/`](service/) with a real repository, and rewrite
   [`AGENTS.md`](AGENTS.md) for it. Keep it to a page.
5. Agree the autonomy matrix with second line **on day one**, not day sixty. In a bank
   that conversation, not the tooling, is what consumes the calendar.

Two deliberate departures from the playbook's examples, both recorded in
[`specs/CHG-2026-014880-showcase-scaffold.md`](specs/CHG-2026-014880-showcase-scaffold.md):
the gates are Python over YAML rather than Rego and Conftest (one home per rule, so the
two cannot drift — Conftest is the swap-in for OPA estates, replacing the Python rather
than duplicating it), and there is no live gateway or deployment target here.

---

*A reference implementation of the Agentic SDLC Playbook v1.0. Describes an implementation
approach and does not constitute legal or regulatory advice.*

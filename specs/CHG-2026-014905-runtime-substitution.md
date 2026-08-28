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

# Spec: the agent runtime as a declared, swappable plane

## Requirements

### R1 — The runtime is configuration, in `.agent/runtimes.yaml`

One `selected:` line, and a declaration per runtime carrying: vendor, invocation shape,
the identifier used to invoke it, whether it needs a gateway credential, and which
context file it reads. Four are declared — GitHub Copilot, Anthropic Claude Code, Google
Gemini CLI, OpenAI Codex.

The file also declares the **contract**: what every runtime is handed (the context, the
skills, the allowlist, the header spec), what it receives per task (task, route, autonomy
tier), and what it must not do. An adapter that has to reshape any of those is a
portability debt rather than an adapter, and naming the contract is what makes that
statement falsifiable.

### R2 — Two invocation shapes, because they are genuinely different

| Shape | Runtime | How it starts | Credential |
|---|---|---|---|
| `assign` | Copilot | Assigned to a bot identity in the VCS | the GitHub token; no provider key |
| `action` | Claude, Gemini, Codex | Runs as a workflow step | gateway token, base URL from `routes.yaml` |

Supporting only the first shape would leave the abstraction untested against the case it
exists for. Both live in `.github/actions/agent-task`.

### R3 — The route comes from the binding, not the caller

The adapter takes a `binding` (`stage2_spec_draft`, `stage6_diagnose`, `stage6_scan`) and
resolves the route from `bindings:` in `.agent/routes.yaml`, asserting the route is
declared. Retargeting a stage to a different tier is therefore a change to the
model-access plane and touches no workflow.

### R4 — Switching prints the blast radius

`scripts/switch_runtime.py` rewrites the `selected:` line and then reports, from `git`
rather than from its own belief, what it wrote — scoped to the file it edits, so an
unrelated dirty tree can neither flatter nor slander the number. It then counts what it
did not touch: skills, eval cases, policy tables, gates, chain artifacts.

A one-line diff is easy to claim and easy to check. The inventory of what did **not**
move is the half that would catch a leak, so it is the half that is printed.

### R5 — Every runtime scores identically, and that is executed

`make swap` switches through all four in turn, re-running the deterministic gates, the
eval suite and the Substitution Test under each, and restores the original selection.
Any score that moves under a runtime change fails the script.

### R6 — Vendor identifiers may appear only in the adapter

Stage 0 collects every `action`, `actor` and `reviewer` identifier from
`.agent/runtimes.yaml` and fails if any appears in a workflow. A vendor's name in prose is
fine; its bot login wired into a stage is the debt.

Stage 5's review request likewise reads the reviewer identity from the selected runtime,
and where a runtime declares `reviewer: null` the step says so rather than reporting a
green check for a review that will not happen.

### R7 — No runtime names a model

`scripts/substitution_test.py` already scans every `.yaml` in the tree for raw model
names, and `.agent/runtimes.yaml` is scanned along with the rest. A vendor name is a fact
about who you buy from. A model name pinned in your repository is a migration you have not
scheduled yet.

## Policy conflicts

**One, and it is not resolved here.**

`policy/autonomy-matrix.yaml` grants tiers to *the agent* as a single actor. Once the
runtime is swappable, "the agent" is four different things with materially different
capabilities, audit surfaces and data-residency positions — Copilot runs inside the VCS
boundary under `github_token`; the hosted runtimes reach a gateway that may terminate in
a different jurisdiction. A tier that is appropriate for one may not be for another.

| Standard | Position |
|---|---|
| `HUM-14` human oversight (EU AI Act Art. 14) | The tier is a property of the *change*, from risk class and environment. Runtime-independent by design. |
| `TPR-05` third-party ICT risk (DORA Ch. V) | Concentration and substitutability are properties of the *provider*. Two providers at the same tier are not equivalent risks. |

**Options, with their trade-offs:**

1. **Leave the matrix runtime-independent.** Simplest, and preserves the property that a
   change's permitted autonomy does not depend on which vendor happens to be selected.
   Understates provider risk.
2. **Add a per-runtime tier ceiling.** Honest about the difference; doubles the size of
   the table every governance forum has to read and re-approve, and the second dimension
   will drift.
3. **Make residency a route concern only.** `gateway/tier-sovereign` already fails closed
   rather than spilling to a shared tenant, so bind sensitive stages to it and leave the
   matrix alone. Narrowest change; relies on bindings being right.

**Owners:** the autonomy matrix is the Head of Engineering with second line; provider
substitutability is Third-Party Risk. **This spec does not choose.** The chain proceeds
with the matrix unchanged and the conflict recorded, which is the Stage 2 control point
working rather than failing.

## Verification

| Requirement | Verified by |
|---|---|
| R1, R7 | Stage 0 context-plane validation; `substitution_test.py` check 5 |
| R2, R3 | `.github/actions/agent-task`; the binding assertion fails loudly on an undeclared route |
| R4 | `make swap RUNTIME=<name>` output |
| R5 | `make swap` — non-zero if any score moves |
| R6 | Stage 0; fails if a workflow contains a declared runtime identifier |

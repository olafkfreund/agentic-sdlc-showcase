---
layout: page
title: The seven stages
permalink: /stages/
lede: >-
  Every stage has a control point, and every control point has a workflow that
  enforces it. Copilot is invoked in exactly one step per stage — the most
  replaceable component in the system.
---

<div class="stage" markdown="1">
### Stage 0 — Foundations

**Control point:** the Substitution Test is scored weekly, and the context plane is
validated as configuration rather than asserted in a document.

Every `SKILL.md` must carry `name`, `description`, `version` and `policy_owner` in its
frontmatter, and every policy YAML must parse. A skill with no named policy owner is a
rule nobody has agreed to.

[`00-foundations.yml`]({{ site.repo_url }}/blob/main/.github/workflows/00-foundations.yml) · `make substitution`
</div>

<div class="stage" markdown="1">
### Stage 1 — Plan

**Control point:** the product owner accepts, and **acceptance is the merge**.

Intent is captured once, by whoever had it, in their own words — problem, who is
affected, success criteria, out of scope, constraints. No solution. Contributors without
version-control experience commit through an MCP connector and never touch git; the gate
is identical for them.

Nothing in the workflow approves anything. It only checks the shape.
</div>

<div class="stage" markdown="1">
### Stage 2 — Design

**Control point:** named policy owners resolve flagged conflicts, before engineering sees
the spec.

On intent merge, the agent is **assigned** the design pass and opens the spec as a pull
request. The spec's `## Policy conflicts` section names standards that cannot both hold,
their owners, and the options with their trade-offs — and **does not resolve them**.

> Finding the conflict during the design pass instead of in a review three weeks later is
> most of the value of the stage. The chain stops at `autonomy_tier: A0` and waits for a
> human with the authority to decide.
</div>

<div class="stage" markdown="1">
### Stage 3 — Build

**Control point:** plan-to-diff conformance, frozen paths, and the autonomy matrix.

A file in the diff that no plan's `## Files` section claims is a departure. The fix is to
update the plan in the same commit, not to argue it in a review comment. A change cannot
self-declare its way past a gate either: `policy/risk-classes.yaml` floors the risk class
from the paths actually touched.
</div>

<div class="stage" markdown="1">
### Stage 4 — Test

**Control point:** the eval pass rate gates configuration changes.

A change to `AGENTS.md`, a skill, a gate or a model route is a change to the agent's
behaviour, and gets regression-tested exactly like the code it produces. Twenty-four
cases, non-interactive, threshold 90%.

CI runs the same three commands `AGENTS.md` tells the agent to run. **If CI and the
agent's loop diverge, the agent is optimising for the wrong signal.**
</div>

<div class="stage" markdown="1">
### Stage 5 — Deploy

**Control point:** severity tally rather than narrative; environment approval; author ≠
approver.

Agent review runs on every pull request, identical for all of them, in three passes
defined in `REVIEW.md` — version-controlled, reviewable, the same next quarter. Where the
pipeline gates, it gates on the machine-readable count of `critical` and `material`
findings, never on the narrative or a model's overall verdict.

Release is attested: signed in-toto provenance from your own CI, plus the gate results
travelling with the artifact so *"which controls ran on the thing that is in production"*
is answerable from the artifact alone.
</div>

<div class="stage" markdown="1">
### Stage 6 — Operate

**Control point:** tier boundaries from version-controlled config, and no production write
access for the agent.

Western Electric rules over a 30-day rolling baseline, unit-tested including the **drift**
case that no simple threshold catches. **No model in detection** — a model that decides
whether something is anomalous is a control you cannot evidence.

| Signal | Tier | What the agent may do |
|---|---|---|
| 2σ | `A0` | Look, and only look. Read-only tools from the MCP allowlist. |
| 3σ | `A2` | Write its diagnosis as an `intent.md` and open it for triage. |

From there the finding re-enters at Stage 1 like any other change, through every gate,
with a human triaging the queue. That is the loop closing.
</div>

## The five planes

| Plane | Here | The point |
|---|---|---|
| Model access | `.agent/routes.yaml` | Routes, never model names. No provider key outside the gateway. |
| Agent runtime | `.github/workflows/`, `.github/actions/assign-copilot/` | Copilot, invoked in one step per stage. The most replaceable component. |
| Context | `AGENTS.md`, `.agent/skills/`, `.agent/mcp-allowlist.yaml` | `.github/copilot-instructions.md` is a five-line pointer, never a source of truth. |
| Control | `policy/`, `scripts/check_*.py`, CODEOWNERS, environments | The advisory layer makes violations rare; the deterministic layer makes them impossible. |
| Evidence | `evidence/`, `ops/otel-collector.yaml`, attestations | Emitted as controls execute. Never reconstructed. |

---
layout: page
title: One change, end to end
permalink: /story/
lede: >-
  A single user story — "let support agents issue a partial refund" — followed from the
  sentence someone said in a meeting to a signed artifact in production. What each stage
  produces, what controls the outcome, and what stays identical when you change vendor.
---

## The story

> **As a** support agent
> **I want to** issue a partial refund on a settled payment
> **so that** I can resolve a billing complaint without escalating to Finance.

Ordinary work. A new endpoint on an established pattern. What follows is not a
description of how it *could* go; it is
[`CHG-2026-014882`]({{ site.baseurl }}/chain/chg-2026-014882-intent/), which is in this
repository, with its header, its gates and its evidence.

The interesting question is not whether an agent can write this endpoint. It can. The
question is **what you can prove about the result six months later, when the person who
reviewed it has left and a regulator is asking.**

---

## Stage 1 · Intent — the sentence, captured once

<div class="stage" markdown="1">
### What is produced

[`intent/CHG-2026-014882-refund-endpoint.md`]({{ site.baseurl }}/chain/chg-2026-014882-intent/) —
problem, who is affected, success criteria, out of scope, constraints. Written by whoever
had the idea, in their own words. **No solution.**

### What controls the outcome

A gate checks the five sections are present. Nothing else. Nothing here approves anything.

Acceptance **is the merge**, by the product owner named in `CODEOWNERS`. There is no
approval field to forge and no workflow step to bypass, because the approval is a git
object signed by GitHub.

### Why it is written this way

An intent that contains a solution has already made the design decision, invisibly, before
anyone with the authority to make it has seen the problem. The most expensive mistakes in
this pipeline are made in the first two hundred words.
</div>

---

## Stage 2 · Design — the conflict surfaces here, or three weeks later

<div class="stage" markdown="1">
### What is produced

A spec, drafted by the agent from the intent, opened as a pull request. It carries the
same `change_id` and the same machine-readable header.

### What controls the outcome

The agent is **assigned** the task — not mentioned — and the assignment is verified. It is
handed the intent, `AGENTS.md`, and the skills the task names. It is told, explicitly:

> **Flag every policy conflict explicitly and prominently. Do not resolve them.**

And a sibling change shows what that produces. Open
[`CHG-2026-014901`, the FX rounding spec]({{ site.baseurl }}/chain/chg-2026-014901-spec/):
its `## Policy conflicts` section names two standards that cannot both hold, their owners,
and the options with their trade-offs — and stops. The chain halts at `autonomy_tier: A0`
awaiting the Group Financial Controller and the DPO.

### Why this is the highest-value stage

**That is the control point working, not failing.** A conflict found during the design pass
costs an afternoon. The same conflict found in review three weeks later costs the sprint,
and found in production costs a remediation programme with a regulator attached.

An agent is unusually good at this specific job — it has read every policy document, it
does not get tired on page forty, and it has no political incentive to leave a conflict
unmentioned. It is also unusually bad at *resolving* the conflict, which is why it is
forbidden from trying.
</div>

---

## Stage 3 · Build — the plan is the contract

<div class="stage" markdown="1">
### What is produced

A [plan]({{ site.baseurl }}/chain/chg-2026-014882-plan/) with a `## Files` section listing
every path it intends to touch, then the diff itself.

### What controls the outcome

Three gates, all arithmetic, none of them consulting a model:

| Gate | Refuses |
|---|---|
| `TRC-01` plan conformance | A file in the diff that no plan's `## Files` section claims |
| `FRZ-01` frozen paths | Any edit to `service/app/v1_legacy/` without a recorded exception |
| `HUM-14` autonomy matrix | A tier above what the matrix permits for the risk class |

And the risk class is not the author's opinion. `policy/risk-classes.yaml` floors it from
the **paths actually touched**:

```yaml
path_floors:
  - { pattern: "service/app/money.py",  min_class: R3, reason: "monetary logic" }
  - { pattern: "service/app/models.py", min_class: R3, reason: "data classification map" }
```

A refund endpoint touches money. It is R3 whatever the header says, and R3 in development
caps the agent at `A2` — edit autonomously within an approved plan, open a pull request,
and nothing further.

### Why it matters

Every one of these would otherwise be a review comment: *"you changed a file the plan
doesn't mention"*, *"that's a bigger change than you've marked it"*. Review comments depend
on the reviewer being awake at 5pm on a Friday. **A control that depends on attention is a
control you cannot evidence.**
</div>

---

## Stage 4 · Test — including the configuration that steers the agent

<div class="stage" markdown="1">
### What is produced

The closed loop — `make build test lint` — plus 24 eval cases that regression-test the
agent's *configuration*.

### What controls the outcome

CI runs the same three commands `AGENTS.md` tells the agent to run. **If CI and the
agent's loop diverge, the agent is optimising for the wrong signal.**

A change to `AGENTS.md`, a skill, a gate or a model route is a change to the agent's
behaviour, and gets regression-tested exactly like the code it produces. That is the idea
most teams have not had yet: your prompt files are production configuration, and they
deserve a test suite.
</div>

---

## Stage 5 · Deploy — findings inform, humans decide

<div class="stage" markdown="1">
### What is produced

An agent review in three passes fixed in [`REVIEW.md`]({{ site.repo_url }}/blob/main/REVIEW.md),
a machine-readable severity tally, a code owner's approval, and a signed release.

### What controls the outcome

Where the pipeline gates, it gates on the **count** of `critical` and `material` findings.
Never on the narrative, never on a model's overall verdict.

| Severity | Effect |
|---|---|
| `critical` · `material` | Blocks merge |
| `minor` | Author's call, recorded |
| `cosmetic` | **Capped at 5 per PR** |

The cosmetic cap exists because an unbounded list of nitpicks trains reviewers to skim,
and a skimmed review is worse than no review — it produces the approval without the
attention.

Then the release is attested: signed in-toto provenance from your own CI, with the gate
results travelling *with* the artifact. Which means the question *"which controls ran on
the thing that is in production"* is answerable from the artifact alone, without asking a
vendor for a report.

### The rule underneath all of it

> **No model in the gate.** A model that can block a merge is a control whose
> effectiveness you cannot evidence.

Ask a model-based gate what its false-negative rate was last quarter and there is no
answer, because there is no stable artefact to have measured. Ask the same of arithmetic
over a YAML table and there is — and the table is reviewable by people who do not read
Python, which is the population that has to sign it.
</div>

---

## Stage 6 · Operate — and the loop closes

<div class="stage" markdown="1">
### What is produced

Western Electric rules over a 30-day rolling baseline. At 3σ, the agent writes its
diagnosis as an `intent.md`, and the change re-enters at Stage 1 like any other.

### What controls the outcome

**No model in detection.** A model that decides whether something is anomalous is a
control you cannot evidence. Detection is deterministic, version-controlled and
unit-tested — including the *drift* case that no simple threshold catches.

| Signal | Tier | What the agent may do |
|---|---|---|
| 2σ | `A0` | Look, and only look. Read-only tools from the allowlist. |
| 3σ | `A2` | Write a diagnosis as an intent, and open it for triage. |

The agent has no production write access at any tier. A human triages: fix now, schedule,
or dismiss — and **dismissals tune the bands**, which is the part that stops the whole
thing becoming noise nobody reads.
</div>

---

## The outcome, and how you control it

Six months later, someone asks:

> *Which production changes touched control `SEC-API-01`, which were agent-authored, at
> what autonomy tier, and who approved each one?*

```bash
python scripts/query_evidence.py --control SEC-API-01
```

Seconds. Not a week of someone reconstructing it from Jira tickets and Slack.

That works because of one design decision taken at the start: **every artifact carries a
machine-readable header, and every gate emits a record keyed to a control id.**

```yaml
change_id: CHG-2026-014882
risk_class: R3
autonomy_tier: A2
controls: [SEC-API-01, CHG-04, DP-11]
data_classification: internal
originator: j.ortiz@example.com
agent_identity: svc-agent-platform     # distinct from the human. Always.
model_route: gateway/tier-balanced     # a route, never a model name
```

`agent_identity` and `originator` are separate fields because segregation of duties
depends on the machine and the person never being the same entity in any record. That one
distinction is what lets you say *"the identity that authored this change could not
approve it"* and mean it structurally rather than procedurally.

The evidence is a **by-product of the control operating**, never a reconstruction. A
reconstruction is a story about a control. Regulators have become quite good at telling
the difference.

---

## Now change vendor

Everything above was produced with GitHub Copilot as the agent runtime. Suppose you want
Anthropic Claude instead — or your procurement function decides for you.

```bash
make swap RUNTIME=claude
```

```
  copilot  ->  claude   (Anthropic Claude Code, Anthropic)

  the swap wrote:  1 file(s), 1 line(s)
                     .agent/runtimes.yaml

  untouched by the swap, counted rather than asserted:
    [ok]   5  skills
    [ok]  24  eval cases
    [ok]   4  policy tables
    [ok]   8  deterministic gates
    [ok]  18  chain artifacts
```

And the outcome is unchanged, because none of what produced it belonged to the vendor:

```
  runtime    gates     evals    subst    cost vs HEAD
  copilot    8/8       24/24    12/12    0+ 0-
  claude     8/8       24/24    12/12    1+ 1-
  gemini     8/8       24/24    12/12    1+ 1-
  codex      8/8       24/24    12/12    1+ 1-
```

### Why the outcome survives

Look back at the story and notice what actually determined each outcome:

| Stage | What decided the outcome | Vendor-owned? |
|---|---|---|
| 1 | Five required sections; a product owner's merge | No |
| 2 | The skill, and the instruction not to resolve conflicts | No — portable markdown |
| 3 | `policy/risk-classes.yaml`, the plan's `## Files`, the frozen list | No — YAML you wrote |
| 4 | 24 eval cases and the closed loop | No |
| 5 | The severity tally, `CODEOWNERS`, an environment approval | No |
| 6 | Western Electric rules in unit-tested Python | No |

The agent drafted, proposed and reviewed. **It decided nothing.** Every outcome was
determined by an artefact in your repository, which is why swapping the drafter changes
one line and no outcome.

That is not an accident of good design taste. It is the direct consequence of one rule
applied everywhere: *models diagnose, propose, draft and review; the decision to allow or
block is arithmetic over policy.*

---

## Why this is unusual

Most agentic-SDLC material describes a **workflow** — which prompts, in which order, with
which tool. That is the replaceable part. This describes a **control layer**, and then
runs it.

Four things follow, and each is checkable rather than asserted:

<div class="cards">
  <div class="card">
    <span class="tag">Provable</span>
    <h3>Every gate has refused</h3>
    <p><code>make negative</code> breaks each protected thing and watches the gate go red.
    A gate verified only by passing is indistinguishable from one that cannot fail.</p>
  </div>
  <div class="card">
    <span class="tag">Portable</span>
    <h3>The swap is executed, not claimed</h3>
    <p>Four vendors, two invocation shapes, identical scores under each. Third-party risk
    gets a demonstration rather than an assurance.</p>
  </div>
  <div class="card">
    <span class="tag">Queryable</span>
    <h3>The supervisory question, in seconds</h3>
    <p>Not a week of reconstruction. The chain of commits <em>is</em> the audit trail — no
    transcript, no chat window, no vendor's session store.</p>
  </div>
  <div class="card">
    <span class="tag">Honest</span>
    <h3>It reports what did not happen</h3>
    <p>Where the agent is unavailable, the step says so. It never produces a green check
    for a control that did not run.</p>
  </div>
</div>

## The value, stated plainly

**For engineering:** the review comments that were always going to be made are made by
code, on every pull request, identically, at 5pm on a Friday.

**For risk and compliance:** the control mapping in `policy/controls.yaml` is the same
table second line signed, executed rather than described, emitting evidence as it runs.
DORA's *"prove the control operated continuously"* is satisfied from your own CI.

**For procurement and third-party risk:** the exit path is one command and one line of
diff, demonstrated on request. Concentration risk stops being a paragraph in a
questionnaire.

**For the board:** you can change your mind. Which, given how fast this field is moving,
is the only durable position available.

<div class="disclaimer">
  <strong>Demo data.</strong> <code>CHG-2026-014882</code> and the evidence quoted here are
  produced by this repository's own pipeline against a synthetic payments service. They are
  not any institution's audit records.
</div>

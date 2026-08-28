---
layout: page
title: Two organisations adopt this
permalink: /adoption/
lede: >-
  Ninety days, step by step, at a tier-1 bank and at a growth-stage payments firm.
  The same repository, the same gates, two very different autonomy matrices — and the
  reason the difference lives in one YAML file rather than in a fork.
---

## Why these two

Both are **illustrative composites**, not clients. Nothing here claims a named institution
uses this repository, because a fabricated customer reference is the fastest way to lose a
room. What *is* real is the regulation each one is reacting to, and those are cited.

| | **Meridian Group** | **Kestrel Pay** |
|---|---|---|
| Shape | Tier-1 European bank, ~4,000 engineers | EMI-licensed payments firm, 60 engineers |
| Binding on them | DORA · EU AI Act · BCBS 239 · SOX ITGC | DORA · EU AI Act · PSD2 · scheme rules |
| Second line | 40 people, own reporting line to the board | One compliance lead, no separate second line |
| What hurts | Twelve weeks to evidence a control to a supervisor | Losing the enterprise deal on the security questionnaire |
| What they fear | A regulator asking a question they cannot answer | Shipping slower than the competitor who has no controls |

They are chosen because **the same three regulations land on both, and land completely
differently.** A framework that only works for one of them is a framework with a market of
one.

---

## The clock that is already running

This is not a 2027 problem. Two dates have passed:

<div class="cards">
  <div class="card">
    <span class="tag">In force</span>
    <h3>EU AI Act, Article 14</h3>
    <p>High-risk obligations became binding on <strong>2 August 2026</strong>. Human
    oversight must be <em>technically embedded in the system</em> — the ability to
    override, interrupt or stop — <strong>not merely described in documentation</strong>.
    Deployers retain automated logs for at least six months.</p>
  </div>
  <div class="card">
    <span class="tag">In force</span>
    <h3>DORA, Articles 28–30</h3>
    <p>Applied from <strong>January 2025</strong>. Documented exit strategies for critical
    ICT services; concentration risk assessed <em>before</em> contracting. 2026 is the year
    supervisors stop reviewing paperwork and ask for proof.</p>
  </div>
  <div class="card">
    <span class="tag">Continuous</span>
    <h3>BCBS 239</h3>
    <p>Data integrity controls are expected to function <strong>continuously, not just
    during audit periods</strong>. A control that only operates when someone is looking has
    not operated.</p>
  </div>
</div>

Read those three together and they describe this repository almost exactly: oversight
enforced in code rather than prose, an exit path you can demonstrate, and evidence emitted
continuously rather than assembled on request.

That is not a coincidence. It is why the repository is shaped this way.

---

# Meridian Group — ninety days

## Day 1–3 · Agree the autonomy matrix. Before any tooling.

**What they do.** Second line, the Head of Engineering and the CISO sit down with
`policy/autonomy-matrix.yaml` — a 20-line table — and argue about it.

```yaml
matrix:                                   # max_tier[risk_class][environment]
  R1: { development: A3, staging: A2, production: A2 }
  R2: { development: A3, staging: A2, production: A1 }
  R3: { development: A2, staging: A1, production: A0 }
```

**Why first.** The playbook is emphatic and it is the advice most often ignored: agree this
on **day one, not day sixty**. In a bank that conversation, not the tooling, is what
consumes the calendar. Teams that install the tooling first spend the next quarter
retrofitting permissions around decisions engineers already made.

**What it produces.** A table a CISO, a Head of Engineering and an auditor can all read and
all sign. Not a policy document — a file the pipeline reads at runtime.

> This is the artefact that satisfies AI Act Article 14. Not a paragraph asserting that
> humans oversee the system: **a machine-readable table the build enforces.** "Technically
> embedded, not merely described" is the test, and a YAML file the gate parses passes it in
> a way a Confluence page cannot.

**Meridian's decision.** R3 in production is `A0` — read and propose only. Their payments
estate is under a s.166 remediation, and second line will not accept an agent editing there
at any tier. **The gate makes that stick without anyone policing it.**

## Day 4–10 · Map the control library

**What they do.** Rewrite `policy/controls.yaml` against Meridian's own control library,
keeping the structure and replacing the contents:

```yaml
  - id: SOD-01
    objective: Segregation of duties
    agentic_implementation: Agent machine identity cannot approve; CODEOWNERS enforced by ruleset
    gate: scripts/check_codeowners.py + .github/workflows/03-gates.yml
    evidence: evidence/codeowners.json
    maps_to: [DORA Ch. II, SOX ITGC]
```

**Why it matters more than it looks.** Every objective names **the gate that enforces it**
and **the evidence it emits**. The Substitution Test's check 6 joins the library against
the gates and fails on any objective with nothing enforcing it — so a control that exists
only on paper cannot survive the file.

**The awkward finding, and it is the point.** Meridian's first pass has 34 control
objectives. Nine have deterministic gates. The other 25 are quarterly attestations by a
named human.

That is not a failure of the exercise; **it is the exercise.** Second line now has a
ranked list of which 25 controls are asserted rather than enforced, which is a better
artefact than the framework was asked to produce.

## Day 11–20 · Path floors, before anyone writes code

**What they do.** Populate `policy/risk-classes.yaml` with the paths that force a minimum
risk class regardless of what a change claims about itself.

```yaml
path_floors:
  - { pattern: "src/payments/settlement/**", min_class: R3, reason: "scheme settlement" }
  - { pattern: "src/**/kyc/**",              min_class: R3, reason: "regulated onboarding" }
  - { pattern: "migrations/**",              min_class: R3, reason: "schema" }
  - { pattern: "policy/**",                  min_class: R3, reason: "control layer" }
```

**Why.** A change that touches settlement is material whatever its header says. Without
floors, risk class is self-declared, and self-declared risk class is a control that fails
exactly when it matters — on the change someone is motivated to get through quickly.

**Verified by breaking it**, not by reading it:

```
  refused         HUM-14  material change declared R1
```

## Day 21–30 · CODEOWNERS, and the rule people skip

```
*                    @meridian/platform-engineering
/policy/             @meridian/platform-engineering @meridian/second-line
/.github/workflows/  @meridian/platform-engineering @meridian/second-line
/intent/             @meridian/product-owners
```

**Second line on `/policy/` is the rule everyone leaves out.** It is also the one that
turns the control mapping from something engineering asserted into something second line
agreed to. Without it, `controls.yaml` is an engineering opinion about compliance.

**The trap this catches.** GitHub **silently ignores** a CODEOWNERS rule whose owner does
not resolve. The rule stays in the file, branch protection still says *require review from
Code Owners*, and the requirement is satisfied by nobody. Meridian has 200 teams and
constant reorganisation; this will happen.

`scripts/check_codeowners.py` calls GitHub's own validator and fails the build on it. It is
a small gate that prevents a control reading as operating while it is not — the failure
mode the whole framework is about.

## Day 31–45 · One team, one service, the whole chain

**What they do.** A single squad runs one real change end to end — intent → spec → plan →
gates → review → attested release. No agent yet. **Humans doing the process manually,
first.**

**Why no agent.** Stage 2.5 of the playbook: run it manually, then codify it as a command,
then trigger it automatically. A team that automates a process it has not performed
automates its misunderstanding of it.

**What they learn.** The `## Policy conflicts` section is where the value is. Their first
spec surfaces a conflict between a data-residency standard and a latency SLO that had been
quietly unresolved for eighteen months, because nobody had been required to write both
down in the same document.

## Day 46–60 · Turn on the agent, at A2, in development only

Now the runtime is selected — one line:

```bash
make swap RUNTIME=copilot
```

The agent drafts specs and implements within an approved plan. It opens pull requests. It
cannot approve one, cannot reach the default branch, and cannot exceed what the matrix
permits.

**Why so late.** Everything above works with no agent at all. That ordering is the
argument: **the control layer does not depend on the agent, so the agent can be introduced
as a productivity change rather than as a governance event.** Meridian's second line
reviews an autonomy tier, not a vendor.

## Day 61–75 · The evidence plane, and the supervisory question

```bash
python scripts/query_evidence.py --control SEC-API-01 --quarter 2026Q2
```

> *Which production changes touched control `SEC-API-01`, which were agent-authored, at
> what autonomy tier, and who approved each one?*

**Before:** three people, most of two weeks, reconstructing from Jira, Bitbucket and
Slack. **After:** seconds, from the repository.

The playbook calls this the single highest-value output of the whole programme, and
Meridian's second line agrees for a reason engineering did not anticipate: it is not the
speed. It is that the answer is **the same every time it is asked**, because it is a query
over records emitted as the controls ran, not a reconstruction assembled by whoever was
free that week.

COSO's 2026 guidance on internal control over generative AI asks for complete,
reconstructable monitoring — prompts, inputs, outputs, model and configuration versions,
human review evidence. BaFin expects a clear audit trail for every automated action. Both
are satisfied by a by-product rather than a project.

## Day 76–90 · Score the exit, and put a date on the debt

```bash
make substitution
```

```
  Substitution Test: 12/12 — PORTABLE
```

**Why this closes the ninety days.** DORA Article 28 requires a **documented exit strategy**
for critical ICT services, and Articles 28–30 require concentration risk to be assessed
*before* contracting. The ECB has found over 30% of significant banks' outsourcing budgets
concentrated on ten providers.

Meridian's third-party risk function has asked every vendor for an exit plan and received
twelve assurances. What they get here instead:

```
  runtime    gates     evals    subst    cost vs HEAD
  copilot    8/8       24/24    12/12    0+ 0-
  claude     8/8       24/24    12/12    1+ 1-
  gemini     8/8       24/24    12/12    1+ 1-
  codex      8/8       24/24    12/12    1+ 1-
```

An exit **executed on demand in a meeting**, with the blast radius counted. Any "no" in the
twelve is a portability debt with a named owner and a date — which is a supervisable
artefact in a way that an assurance is not.

---

# Kestrel Pay — the same repository, different everywhere it matters

Sixty engineers. The same three regulations. A completely different shape.

## What changes

### The autonomy matrix moves up

```yaml
matrix:
  R1: { development: A3, staging: A3, production: A2 }   # Meridian: A3/A2/A2
  R2: { development: A3, staging: A2, production: A2 }   # Meridian: A3/A2/A1
  R3: { development: A2, staging: A2, production: A0 }   # R3 production unchanged
```

Kestrel accepts more autonomy in staging and for standard changes. **R3 in production stays
`A0` in both**, because settlement and KYC are where a payments firm dies, and firm size
does not change that.

### `CODEOWNERS` cannot pretend to have a second line

```
*            @kestrel/engineering
/policy/     @kestrel/engineering @kestrel/compliance-lead
/intent/     @kestrel/product
```

One compliance lead, named. **Naming one real person beats naming a team that does not
exist** — GitHub silently ignores the second, and the gate catches it.

### The `production` environment is the whole of change management

Meridian has a CAB. Kestrel has a required reviewer on a GitHub environment with
`prevent_self_review` on. **Both satisfy the same control objective**, and the second one
does it without a weekly meeting.

### The gates that earn their keep are different

| | Meridian | Kestrel |
|---|---|---|
| Most valuable | `SOD-01` — 200 teams, constant reorg, rules that silently resolve to nobody | `FIN-02` — a `float` on a monetary field is an existential bug at their margins |
| Second | `TRC-01` — plan-to-diff conformance replaces the review comment nobody has time to make | `SEC-API-01` — the security questionnaire that gates every enterprise deal |
| Barely used | `FRZ-01` — no frozen legacy yet | `HUM-14` at R1 — everything is A3 anyway |

### The commercial driver is the opposite

Meridian adopts this because a supervisor will ask. **Kestrel adopts it because a customer
will ask** — and being able to answer the enterprise security questionnaire with a URL and
a command that runs in front of the buyer is worth more to them than the internal
efficiency.

## What does not change

Not one line of `scripts/`. Not one gate. Not the artifact header, the evidence schema, the
eval runner, the detector, or the Substitution Test.

**Everything that differs between a tier-1 bank and a sixty-person payments firm lives in
four YAML files.** That is what makes this a framework rather than a template — and it is
checkable rather than asserted:

```bash
diff -r meridian/scripts kestrel/scripts     # empty
diff meridian/policy/autonomy-matrix.yaml kestrel/policy/autonomy-matrix.yaml
```

---

## The four files you will actually edit

| File | What it is | Who signs it |
|---|---|---|
| `policy/autonomy-matrix.yaml` | What the agent may do, per risk class and environment | Head of Engineering **and** second line |
| `policy/risk-classes.yaml` | Which paths force a risk floor regardless of what a change claims | Architecture and second line |
| `policy/controls.yaml` | Your control library, each objective mapped to its gate and evidence | Second line owns it |
| `CODEOWNERS` | Who must approve what. The one that silently fails | Platform, with second line on `/policy/` |

Plus `AGENTS.md` rewritten for your codebase — keep it to a page — and `service/` replaced
by a real repository.

## The order that matters

1. **Autonomy matrix with second line. Day one.** Everything else is engineering work.
2. **Control library mapped to gates.** Discovering which controls have no gate is the
   deliverable, not a setback.
3. **Path floors**, so risk class cannot be self-declared.
4. **CODEOWNERS with second line on the control layer.**
5. **One team, one service, the whole chain — by hand.**
6. **Then** the agent, at the tier the matrix already permits.
7. **Score the Substitution Test**, and put a name and a date on every "no".

Steps 1–5 involve no agent at all. If step 6 never happened, an organisation completing
1–5 would still be materially better governed than it was — and that, rather than any claim
about productivity, is the argument worth making to a board.

<div class="disclaimer">
  <strong>Meridian Group and Kestrel Pay are illustrative composites.</strong> They are not
  clients, and nothing here should be read as a claim that any named institution uses this
  repository. The regulations, deadlines and supervisory expectations cited are real and
  linked. This describes an implementation approach and does not constitute legal or
  regulatory advice.
</div>

## Sources

- [EU AI Act, Article 14 — Human Oversight](https://artificialintelligenceact.eu/article/14/)
- [EU AI Act high-risk compliance deadline, 2 August 2026 — Cloud Security Alliance](https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-ai-act-high-risk-compliance-deadline-20/)
- [DORA Article 28 — documented exit strategies for ICT third-party services](https://www.kiteworks.com/third-party-risk/dora-article-28-exit-strategies/)
- [DORA for banks 2026 — ECB supervision and ICT roadmap](https://www.regulation-dora.eu/banking)
- [DORA third-party ICT risk, Articles 28–30](https://www.cyadviso.com/dora-third-party-ict-risk)
- [AI audit trail requirements — 2026 checklist for finance and banking](https://www.kognitos.com/blog/ai-audit-trail-requirements-2026-checklist/)
- [AI agent governance as a board-level question](https://crunchspark.com/ai-agent-governance-cfo-2026.html)

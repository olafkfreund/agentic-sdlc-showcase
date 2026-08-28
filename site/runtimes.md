---
layout: page
title: Switching the agent vendor
permalink: /runtimes/
lede: >-
  GitHub Copilot, Anthropic Claude, Google Gemini, OpenAI Codex — one command, one
  line of diff, and the repository re-scores itself under each to prove nothing else
  moved.
---

## The question third-party risk asks first

> If you replaced your agent vendor on Monday, what would you have to rebuild?

Every vendor's answer is "nothing". `DORA Ch. V` makes it a regulatory question rather
than a preference, and *"look at these two files and you'll see it would be fine"* is not
an answer. So here it is executed instead:

```bash
make swap
```

```
  Scoring the repository under each agent runtime:

  runtime    gates     evals    subst    cost vs HEAD
  ---------  --------  -------  -------  ------------
  copilot    8/8       24/24    12/12    0+ 0-
  claude     8/8       24/24    12/12    1+ 1-
  gemini     8/8       24/24    12/12    1+ 1-
  codex      8/8       24/24    12/12    1+ 1-

  Identical under every runtime, because none of it belongs to a vendor:
     5 skills          24 eval cases       4 policy tables
     8 gates           18 artifacts        9 control objectives
```

The deterministic gates, the eval suite and the Substitution Test are re-run under each
runtime. **A score that moves under a vendor change is a portability debt, not a
refactor**, and the script exits non-zero if one does.

## Switching to one

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

A one-line diff is easy to claim and easy to check, so the interesting half of that
report is the second one. If a swap ever starts touching a skill or a policy table, this
prints it rather than letting it pass as a refactor.

## Two invocation shapes, because they are genuinely different

| Shape | Runtime | How it starts | Credential |
|---|---|---|---|
| `assign` | GitHub Copilot | Assigned to a bot identity in the VCS | the GitHub token — **no provider key** |
| `action` | Claude, Gemini, Codex | Runs as a workflow step | gateway token, base URL from `routes.yaml` |

Supporting only the first would leave the abstraction untested against the case it exists
for. Both live in one adapter, [`.github/actions/agent-task`]({{ site.repo_url }}/blob/main/.github/actions/agent-task/action.yml),
and every stage that hands work to an agent goes through it.

```yaml
# .agent/runtimes.yaml — the runtime plane (playbook §5.2), entire
selected: copilot

runtimes:
  copilot:
    vendor: GitHub
    invocation: assign
    actor: copilot-swe-agent
    needs_gateway: false
  claude:
    vendor: Anthropic
    invocation: action
    action: anthropics/claude-code-action@v1
    needs_gateway: true
```

## The three rules that keep it honest

### No runtime names a model

A vendor name is a fact about who you buy from. **A model name pinned in your repository
is a migration you have not scheduled yet.** Which model serves a route is the gateway's
decision, made in `.agent/routes.yaml`, and `substitution_test.py` scans every YAML in the
tree — this one included — for raw model names.

### No stage names a vendor

Stage 0 collects every `action`, `actor` and `reviewer` identifier from
`.agent/runtimes.yaml` and **fails the build if any appears in a workflow**. A vendor's
name in prose is fine; its bot login wired into a stage is the debt. Without that check
the abstraction would quietly rot back into a hard-coded vendor within two quarters.

### A runtime that cannot run says so

The hosted runtimes take their credential from a gateway this repository deliberately does
not have. Selected without one, the stage writes a plain summary saying no agent took the
task and emits a warning. It does not fail the build — a missing advisory layer is not a
control failure — and **it does not report success**.

> A green check for a control that did not run is precisely the failure mode this
> playbook is about.

## What this costs, honestly

Copilot is the only runtime here that needs no provider credential, because GitHub is
already the version control system. That convenience is exactly why it is the one worth
being able to leave.

There is also an unresolved policy conflict, recorded rather than hidden. The autonomy
matrix grants tiers to *the agent* as a single actor; once the runtime is swappable, that
is four things with different audit surfaces and residency positions. The spec names the
conflict, its two competing standards, their owners and three options — and
[does not resolve it]({{ site.baseurl }}/chain/chg-2026-014905-spec/). That is the Stage 2
control point working.

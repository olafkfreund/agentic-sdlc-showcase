---
layout: page
title: The Substitution Test
permalink: /substitution/
lede: >-
  Twelve checks, executed against the repository rather than self-assessed. Nothing
  scores a mark for a document that merely claims a property.
---

## The question

> If you replaced your agent vendor on Monday, what would you have to rebuild?

If the answer is *"the context, the policy, the evidence and the audit trail"*, the
operating model was never yours. The Substitution Test is Appendix C of the playbook, and
here it is a script rather than a questionnaire.

```bash
make substitution
```

```
  Substitution Test: 12/12 — PORTABLE — you can change your mind,
  which is the only durable position.
```

## The twelve

| # | Check | How it is scored |
|---|---|---|
| 1 | Repository context lives in `AGENTS.md`, not a vendor filename | The tree is scanned for `.cursorrules`, `.windsurfrules`, `GEMINI.md` and friends; the Copilot pointer must stay under 80 words |
| 2 | Skills are portable markdown with a named policy owner | Every `SKILL.md` frontmatter is parsed and its `policy_owner` required |
| 3 | Tool access is an allowlist, deny by default | `.agent/mcp-allowlist.yaml` is read and its servers counted |
| 4 | All model calls traverse a gateway you control | Every scannable file is searched for a direct provider endpoint |
| 5 | Model choices are routes, not model names | A regex hunts raw model names across the whole tree — including the file you are least likely to check |
| 6 | Every must-hold control has a deterministic gate | `policy/controls.yaml` is joined against the gates that exist |
| 7 | Telemetry in OpenTelemetry, normalised at your collector | The collector config must normalise the GenAI attributes |
| 8 | Approval gates in your CI and VCS | Workflows, CODEOWNERS and an environment approval gate must all be present |
| 9 | Agent identity distinct from human identity | Both `agent_identity` and `originator` are required and validated separately |
| 10 | An eval suite can qualify a new model in a day | The suite must hold 20–50 cases and run non-interactively |
| 11 | The artifact chain lives in your repository | Chains are walked end to end; every header must be valid |
| 12 | A signed evidence trail without asking a vendor | The release workflow must produce signed in-toto provenance from your own CI |

## Why it is scored by code

A self-assessed portability questionnaire returns twelve yeses. Every time.

The interesting checks are the ones that are easy to believe you pass. Check 5 scans
`.py`, `.yaml`, `.yml`, `.sh`, `.toml` and `.json` across the entire tree for a raw model
name, and the detector deliberately excludes itself, because it holds the pattern it
hunts for. Check 6 does not ask whether you have a control library; it joins the library
against the gates and fails on any control objective with nothing enforcing it.

> Any "no" is a portability debt with a named owner and a date. Not a failure — a debt.
> The point of scoring it weekly is that the trend is the signal.

## What Copilot's replaceability actually costs

Copilot is the agent runtime here, deliberately. The honest way to argue that an
operating model survives a change of vendor is to use a specific vendor's agent and keep
every asset in open formats.

It is invoked in exactly one place — [`.github/actions/assign-copilot`]({{ site.repo_url }}/blob/main/.github/actions/assign-copilot/action.yml) —
plus the review request in Stage 5. Swapping it is an edit to those two files. The
context, the skills, the policy, the gates and the evidence do not move.

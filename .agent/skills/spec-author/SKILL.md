---
name: spec-author
description: Draft a spec.md from an accepted intent.md with all organisational policy
  skills loaded. Use when an intent has merged and the design pass is due.
version: 1.0.0
policy_owner: Chief Architect
paired_gate: scripts/check_artifact_header.py
control: CHG-04
stage: 2
---

# Authoring a spec

Stage 2. Requirements and design compress into one pass, with policy applied while the
spec is written rather than discovered in a review three weeks later.

## Load first

Every policy skill applicable to the domain: `secure-api-review`, and any data
protection, accessibility, or regulatory skill in `.agent/skills/`. Read the intent.
Read `AGENTS.md`. Read the existing code you are about to design against.

## Draft

`specs/<change_id>-<slug>.md`, same `change_id` as the intent it derives from.

```
## Summary            one paragraph
## Requirements       numbered, each traceable to a success criterion in the intent
## Design             the approach, and the alternatives rejected with reasons
## Data               entities touched, and their classification
## Policy conflicts   see below — this is the important section
## Non-functional     latency, volume, availability, retention
## Test strategy      how the requirements will be proven
```

## The policy conflicts section

**This is the highest-value output of the stage.** Flag explicitly and prominently every
point where two policies cannot be jointly satisfied, or where a policy cannot be met
within the constraints. For each:

- the two policies, named, with their owners
- what each requires
- why they cannot both hold here
- the options, with the trade-off each carries

Do not resolve it. Do not pick one and move on. Do not soften the language so it reads
smoothly. A named policy owner resolves it with the product owner **before engineering
sees the spec** — that is the entire point of surfacing it here rather than in a review.

If there are no conflicts, say so explicitly: `## Policy conflicts\n\nNone identified.`
An absent section reads as an unperformed check.

## Rules

- R3 changes require architect sign-off before Build. Note it in the spec.
- Never invent a requirement the intent does not support. If the intent is silent on
  something the design needs, add it to `## Open questions` and stop.

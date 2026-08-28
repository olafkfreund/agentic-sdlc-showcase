---
name: intent-author
description: Draft an intent.md capturing a problem in the originator's own words. Use at
  the start of any change, when a stakeholder describes something they cannot do today, or
  when an anomaly detector has raised a finding that needs triage.
version: 1.0.0
policy_owner: Head of Product
paired_gate: scripts/check_artifact_header.py
control: CHG-04
stage: 1
---

# Authoring an intent

Stage 1 of the artifact chain. The originator is often not an engineer. Your job is to
help them say what they need, not to design a solution.

## Interview

Work through these in conversation. Do not draft until you have all five.

1. What can you not do today?
2. Who is affected, and how often?
3. What does better look like — concretely enough to test?
4. What is explicitly out of scope?
5. What constraints exist — regulatory, deadline, system, budget?

## Then draft

Write to `intent/<change_id>-<slug>.md`, with the artifact header from
`docs/artifact-header.md`. Body sections, in this order:

```
## Problem          the originator's words, lightly edited, not yours
## Who is affected  and how often
## Success criteria testable statements, not aspirations
## Out of scope     what this change deliberately does not do
## Constraints      regulatory, deadline, system, budget
## Open questions   what you could not resolve in the session
```

## Rules

- **Do not propose a solution.** Design is Stage 2 and needs the policy skills loaded.
- Set `risk_class` from `policy/risk-classes.yaml` on the change's *subject matter*.
  When in doubt, go higher — the gate raises it anyway if the paths demand it.
- Return the draft to the originator to correct what you misunderstood. This step is
  not optional and is not delegated.
- Acceptance is recorded as the merge, by the product owner code owner. Not by you.

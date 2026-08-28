<!--
Read CONTRIBUTING.md first. This repository is governed by the process it demonstrates,
so the gates will refuse a pull request that skips the chain — no code without a plan,
no plan without a spec, no spec without an intent.
-->

## What this changes, and why

<!-- One paragraph. The problem, not the diff. -->

## The chain

- Intent: `intent/CHG-____-______-*.md`
- Spec:  `specs/CHG-____-______-*.md`
- Plan:  `plans/CHG-____-______-*.md`

The plan's `## Files` section claims every path in this diff. A file changed that the plan
does not claim is a departure — update the plan in this commit rather than arguing it in a
review comment.

## Verification

Paste the **literal** output. If a test failed, fix the code, not the test. If a gate
failed, fix the change, not the gate.

```
$ just check

```

- [ ] `just check` — build, test, lint, gates
- [ ] `just negative` — every gate still refuses
- [ ] `just eval` — if this touches `AGENTS.md`, `.agent/`, `policy/` or `scripts/`

## Anything a reviewer should push back on

<!-- Shortcuts taken, alternatives rejected, anything you are unsure about. A pull request
     with nothing to push back on usually means the interesting part is undocumented. -->

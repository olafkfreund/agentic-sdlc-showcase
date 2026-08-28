# Contributing

This repository is governed by the process it demonstrates. That is the point, and it
means a contribution here looks different from most.

## Before code, an artifact chain

No code merges without a plan; no plan without a spec; no spec without an intent.
`scripts/check_artifact_header.py` enforces it, and `scripts/check_plan_conformance.py`
refuses any file in your diff that no plan's `## Files` section claims.

1. **`intent/CHG-YYYY-NNNNNN-slug.md`** — the problem, who is affected, success criteria,
   out of scope, constraints. **No solution.** An intent containing a solution has made
   the design decision before anyone with the authority to make it has seen the problem.
2. **`specs/`** — the requirements, and a `## Policy conflicts` section. If two standards
   cannot both hold, name them, name their owners, give the options with their trade-offs,
   and **do not resolve them**. That section is the highest-value output of the stage.
   If there are genuinely no conflicts, say so explicitly — an absent section is
   indistinguishable from an unperformed check.
3. **`plans/`** — approach, `## Files`, sequence with a verification per step, risks,
   what you rejected and why, tests, rollback.

Each carries the header in `docs/artifact-header.md`. `model_route` is a gateway route,
never a model name.

## Then the loop

```bash
nix develop          # or: python -m venv .venv && .venv/bin/pip install -e '.[dev]'
just check           # build, test, lint, gates — the four commands AGENTS.md tells the agent to run
just negative        # every gate must still refuse
```

Paste the literal output into your pull request. **If a test fails, fix the code, not the
test. If a gate fails, fix the change, not the gate.**

## The rules that are not negotiable

- **Money is `decimal.Decimal`.** Never `float`, never `round()` on a monetary value.
- **Every state-changing endpoint emits an audit event.**
- **Fields classified `personal` never reach a log line or an error message.**
- **`service/app/v1_legacy/` is frozen.**
- **No model in a gate.** Models diagnose, propose, draft and review. The decision to
  allow or block is arithmetic over `policy/`. A model that can block a merge is a
  control whose effectiveness you cannot evidence.

## Changing the agent's configuration

`AGENTS.md`, `.agent/skills/`, `.agent/routes.yaml`, `.agent/runtimes.yaml` and `policy/`
are production configuration. A change to any of them is a change to the agent's
behaviour and is gated on the eval suite (`just eval`). Add a case rather than loosening
the threshold.

## If a review finds the same mistake twice

The correction goes into `AGENTS.md` as part of that review, so it is caught from the next
pull request onward. Procedural corrections go into the relevant `SKILL.md`; anything that
must always hold also gets a gate in `policy/`. A repeat finding that never reaches the
context file is a review that will keep finding it forever.

## Licence

Contributions are accepted under Apache-2.0. See `LICENSE` and `NOTICE`.

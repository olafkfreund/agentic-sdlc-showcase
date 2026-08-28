---
change_id: CHG-2026-014903
risk_class: R3
autonomy_tier: A2
controls: [CHG-04, TRC-01, SOD-01, TPR-05]
data_classification: public
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---

# Spec: public showcase site, and a real agent invocation

## Requirements

### R1 — The site is generated from the repository, not written alongside it

`site/build_pages.py` emits `site/playbook.md` and one page per artifact in the chain,
reading them through `scripts/artifacts.py` — the same parser the gates use, so the site
and the gates cannot disagree about what an artifact is. Generated files are git-ignored.

The §6.2 header is rendered as a fenced YAML block rather than consumed as Jekyll front
matter. Consuming it would hide the field that makes the chain queryable, on the page
whose purpose is to show it.

### R2 — The Jekyll engine, Gruvbox dark, no third-party assets

`actions/jekyll-build-pages` builds `site/` and `actions/deploy-pages` publishes it. One
hand-written stylesheet carrying the Gruvbox dark palette, including the Rouge token
colours. No CDN, no font service, no analytics: a page arguing for supply-chain
discipline should not pull four hosts to render.

### R3 — The agent is invoked, not mentioned

`.github/actions/assign-copilot` resolves `copilot-swe-agent` through
`suggestedActors(capabilities: [CAN_BE_ASSIGNED])`, assigns the issue via
`replaceActorsForAssignable`, and then **re-reads the assignees to confirm it landed**.

Where the agent is unavailable it writes a plain step summary saying so and emits a
warning. It does not fail the build — a missing advisory layer is not a control failure —
and it does not report success either.

This is one composite action used by Stage 2 and Stage 6. With the Stage 5 review request
that is two files touching the agent runtime in the whole repository, which is what makes
the Substitution Test's answer for check 5 a fact rather than an aspiration.

### R4 — The CODEOWNERS gate reaches GitHub's validator

`scripts/check_codeowners.py` degrades to an offline file check when it cannot reach the
API, and prints that it has. In `03-gates.yml` it ran with no `GH_TOKEN`, so it *always*
degraded while `policy/controls.yaml` documented it as calling GitHub's own validator.
The token is now passed.

This is the repository's own thesis turned on itself: a control that reads as operating,
in the control that exists to catch controls that read as operating.

### R5 — The headline numbers are regression-tested

`scripts/tests/test_readme_claims.py` parses the README's score block and asserts each
number against the tree: eval case files, `expect_red` invocations in the negative suite,
`check_NN` functions in the Substitution Test. It also asserts each score is `n/n`.

### R6 — Ownership moves to the account hosting the repository

`CODEOWNERS` names `@olafkfreund`. An owner that does not resolve is silently ignored by
GitHub, so leaving the previous EMU identity in place would have left every rule in the
file requiring nobody — which `check_codeowners.py` now actually detects, per R4.

## Policy conflicts

**None identified.** Stated explicitly rather than omitted: an absent section is
indistinguishable from an unperformed check.

The one considered and dismissed: publishing the artifact chain makes the demo change ids
and synthetic evidence public. They are labelled as demo output in the README, the site
footer, the query tool and the bundle, and the payload is a synthetic payments service
with no real data. `data_classification: public` on this change is therefore correct
rather than convenient.

## Departures from the playbook's examples

Recorded here so they are not discovered later:

- The site lives in `site/` rather than `docs/`, because `docs/` already holds repository
  documentation that the plan-conformance gate exempts. Merging the two would either
  publish files that are not pages or exempt files that should not be.
- `permalink` is set per page rather than relying on directory structure, so a generated
  page's URL is stable if its source file is renamed.

## Verification

| Requirement | Verified by |
|---|---|
| R1 | `python site/build_pages.py` regenerates cleanly; chain page count matches `artifacts.all_artifacts()` |
| R2 | The Pages workflow builds and deploys; the site renders with no external request |
| R3 | The assign step re-reads assignees and reports honestly on both paths |
| R4 | `check_codeowners.py` reports `validator=github` in its evidence record in CI |
| R5 | `scripts/tests/test_readme_claims.py`, in `make test` |
| R6 | `make gates` — SOD-01 passes against GitHub's validator |

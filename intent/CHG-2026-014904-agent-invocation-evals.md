---
change_id: CHG-2026-014904
risk_class: R3
autonomy_tier: A2
controls: [TPR-05, HUM-14, CHG-04]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---

# Intent: regression-test the agent invocation path itself

## Problem

The eval suite regression-tests the *configuration that steers* the agent — `AGENTS.md`,
the skills, the routes, the policy tables. It does not test the code that **invokes** the
agent.

That code is now the thing most likely to fail silently. `.github/actions/assign-copilot`
resolves a bot id, performs a GraphQL mutation, and re-reads the assignees to confirm the
assignment landed. Each of those three can degrade independently, and two of the three
degrade *quietly*: an API that returns success while adding no assignee, and a
`suggestedActors` query that stops returning the bot when a seat or a policy changes.

There is a specific asymmetry worth naming. A failure in the deterministic layer is loud —
a red check, a blocked merge. A failure in the agent-invocation layer is silent, because
its correct behaviour when the agent is unavailable is *also* to pass. The repository
argues at length that a control which reads as operating while it is not is the failure
worth fearing, and then ships one.

## Who is affected

- Anyone demonstrating Stages 2 and 6, who currently finds out the invocation is broken by
  watching nothing happen.
- Anyone adopting this repository, whose first agent hand-off is the moment the path is
  first exercised.
- Second line, if the autonomy tier carried on an agent hand-off is ever relied on as
  evidence — an unassigned issue and an assigned one are indistinguishable in the
  workflow's own logs today.

## Success criteria

1. The eval suite covers the invocation path: that the agent is handed work by
   **assignment** and never by a bare `@copilot` mention; that the assignment is verified
   after the mutation; and that an unavailable agent produces a warning rather than a
   silent pass.
2. Every issue a workflow opens for the agent carries an `autonomy-A*` label matching the
   tier stated in its body, and a case fails if the two disagree.
3. The suite still runs non-interactively in `--mode static`, with no network call and no
   GitHub token, so it stays runnable on a fork.
4. `make eval` stays green and the pass-rate threshold is unchanged.

## Out of scope

- Testing GitHub's own API behaviour. The cases read this repository's workflows and
  action definitions; they do not call GitHub.
- Changing what the agent is asked to do at any stage. This is about whether the ask
  arrives, not what it says.
- Any change to `policy/autonomy-matrix.yaml`. If a tier is wrong, that is a separate
  change with its own record.

## Constraints

- Cases are YAML in `.agent/evals/cases/`, in the existing format. No new runner mode and
  no new dependency.
- The existing 24 cases must keep passing unchanged; this adds coverage rather than
  reshaping the suite.
- `scripts/tests/test_readme_claims.py` asserts the README's eval count against the case
  files, so the README moves in the same change.

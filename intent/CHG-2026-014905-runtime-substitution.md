---
change_id: CHG-2026-014905
risk_class: R3
autonomy_tier: A2
controls: [TPR-05, CHG-04, TRC-01, HUM-14]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---

# Intent: make the vendor swap demonstrable rather than asserted

## Problem

The repository claims the agent runtime is its most replaceable component, and scores
itself 12/12 on the Substitution Test partly on that basis. But the claim is only
inspectable: a reader has to read two workflow files and take on trust that swapping
vendor would not ripple further.

That is the weakest kind of evidence this repository accepts anywhere else. Every other
claim here is executed — the gates are proven by being made to refuse, the eval suite is
run rather than described, the Substitution Test is scored from the tree rather than
self-assessed. Portability is the one claim still resting on a paragraph.

It is also the claim that matters most commercially. "What happens when we want to move
off this vendor" is the first question a bank's third-party risk function asks, and
`DORA Ch. V` makes it a regulatory one rather than a preference. An answer of *"look at
these two files and you'll see it would be fine"* is not an answer.

There is a second, quieter problem. Copilot is invoked by **assignment** to a bot
identity in the VCS; every other runtime worth considering is invoked as a **workflow
step** with a credential. Those are different shapes. A design that has only ever hosted
the first shape has not been tested against the abstraction it claims to have.

## Who is affected

- Third-party risk and procurement, who need the exit path evidenced rather than described.
- Anyone adopting this who has already standardised on a different vendor and currently
  has to reverse-engineer where to cut.
- The maintainer, who otherwise discovers the abstraction leaks on the day it is needed.

## Success criteria

1. The agent runtime is declared as configuration, and switching vendor is a single
   command whose entire diff is one line.
2. At least one runtime of each invocation shape is supported — an identity in the VCS,
   and a hosted step taking its credential from the gateway.
3. Switching prints the blast radius: what the swap wrote, and the count of skills,
   policy tables, gates, eval cases and chain artifacts it did not touch.
4. The repository re-scores itself under every runtime — gates, evals and the
   Substitution Test — and the scores are identical. A score that moves is a portability
   debt, not a refactor.
5. A stage that wires a vendor identifier directly fails Stage 0, so the abstraction
   cannot quietly rot back into a hard-coded vendor.
6. No runtime names a model. Which model serves a route stays the gateway's decision.

## Out of scope

- Running a non-Copilot runtime live here. Those take their credential from a gateway
  this repository deliberately does not have. The adapter reports plainly that no agent
  took the task rather than pretending one did.
- Choosing between vendors, or benchmarking them. The point is being able to change your
  mind, not having the right opinion today.
- Any change to the autonomy matrix, the risk classes or the control mapping. If a
  runtime needs a different tier, that is a separate change with its own record.

## Constraints

- The existing Substitution Test stays at twelve checks. Appendix C has twelve; inventing
  a thirteenth to score better would be exactly the self-assessment this test replaces.
- No new dependency, and no runner may hold a direct provider API key.
- The context plane must not fork. A runtime that prefers its own instructions file is
  configured to read `AGENTS.md`; a second context file in the tree fails Substitution
  Test #1.

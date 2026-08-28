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

# Intent: publish the showcase, and let the agent actually run it

## Problem

The repository is the argument, but it can only be read by someone who clones it and runs
`make`. That is the wrong first thirty seconds for the audience this exists for — a head
of engineering, a CISO, a second-line reviewer. There is no public entry point.

Two related things are also untrue rather than merely absent:

1. The workflows *mention* the agent (`@copilot` in an issue body) where the documentation
   says they *invoke* it. A mention is not an invocation; the Copilot coding agent starts
   when it is assigned. `docs/org-prerequisites.md` records this as an org limitation, but
   the limitation no longer applies on the account now hosting the repository.
2. The README's headline scores were written by hand and had drifted: it claimed 23 evals
   over a suite of 24, and ten negative proofs over twelve.

The second is small and embarrassing in a specific way. A repository whose entire argument
is that a control must not merely *read* as operating cannot ship a score that merely
reads as true.

## Who is affected

- Anyone evaluating the operating model without cloning it — the primary audience.
- Whoever demonstrates this, who currently has to explain why the agent steps do nothing.
- The maintainer, who inherits any claim on the page that the tree stops supporting.

## Success criteria

1. A public site at `https://olafkfreund.github.io/agentic-sdlc-showcase/` renders the
   argument, the stages, the gates, the Substitution Test and the artifact chain.
2. The site publishes the playbook and the chain **from the files on disk**, so a page
   cannot drift into disagreeing with the repository it describes.
3. The agent is genuinely invoked — assigned, and the assignment verified — in Stages 2
   and 6, with an honest report where the agent is unavailable.
4. Every headline number in the README is regression-tested against the tree.
5. `make build test lint gates`, `make eval`, `make substitution` and `make negative` all
   stay green, and this change passes its own gates like any other.

## Out of scope

- A live gateway or a deployment target. The repository still has neither, deliberately.
- Rewriting the playbook text. It is published as it is on disk, H1 excepted.
- Any custom domain, analytics, or third-party asset on the page.

## Constraints

- The site must not become a second source of truth. Derived pages are generated, and
  generated pages are git-ignored.
- An artifact's §6.2 header is YAML the gates parse. It must not become Jekyll front
  matter, because the header is the thing worth showing.
- No external CSS or JavaScript. One stylesheet, Gruvbox dark, no build step beyond Jekyll.

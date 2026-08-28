---
change_id: CHG-2026-014910
risk_class: R2
autonomy_tier: A2
controls: [TPR-05, HUM-14, CHG-04]
data_classification: public
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---

# Intent: show how an organisation arrives at this, not only what it does

## Problem

The site explains the pipeline thoroughly and answers a question nobody asked first.

`/story/` follows one change through seven stages — excellent for an engineer, and it
assumes the pipeline already exists. The reader who decides whether this gets adopted is
usually not that engineer. It is a head of engineering with a DORA deadline, a second-line
reviewer who has read the AI Act, or a founder answering an enterprise security
questionnaire. Their question is not *how does a change flow through this*. It is **what do
I actually do on Monday, in what order, and which of my problems does each step solve**.

Nothing on the site answers that. The README's "Adopting this" section is five bullets.

There is a second gap, and it costs credibility rather than clarity. The material argues
from principle — controls should be enforced not asserted, evidence should be a by-product
— without ever naming the regulation that makes those principles binding, or the date. A
reader in a regulated firm knows those dates. Arguing from first principles to an audience
that is already under an enforcement clock reads as naive.

## Who is affected

- The person who decides whether to adopt this, who is not the person who reads the code.
- Whoever presents it, who currently improvises the sequencing and therefore varies it.
- Smaller firms, who assume a framework shaped around a tier-1 bank is not for them.

## Success criteria

1. A step-by-step adoption sequence with, at each step, what is done, what it produces and
   why that step comes where it does.
2. Two organisations of very different size and shape, so the reader can locate themselves.
3. Every regulatory claim cited to a real, linked source with its real date.
4. It is explicit about what changes between the two and what does not — and the "does not"
   is checkable rather than asserted.
5. No claim, express or implied, that a named institution uses this.

## Out of scope

- Pricing, effort estimates or a delivery methodology.
- Any real client engagement. The organisations are composites and say so.
- Changing the pipeline. This describes what exists.

## Constraints

- **A fabricated customer reference is not acceptable at any level of usefulness.** The
  organisations must be labelled composites, prominently, at the top and again at the end.
- Regulatory claims must be checkable. Anything not citable gets cut rather than softened.

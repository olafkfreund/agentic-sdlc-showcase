---
change_id: CHG-2026-014922
risk_class: R2
autonomy_tier: A2
controls: [CHG-04, TRC-01]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---

# Intent: a chain that stops should say so

## Problem

Three chains in this repository stop before a plan. The published chain page lists all three
alongside the completed ones, with no indication that they are not in progress.

`CHG-04` does not catch it, and the reason is precise: it enforces the chain **backwards**
— a plan implies a spec implies an intent — and never forwards. An intent that never becomes
a spec passes silently, and goes on passing forever.

**Stopping is legitimate.** All three of these stopped for a good reason:

- **`CHG-2026-014901`** hit a policy conflict its spec could not resolve, and is waiting on
  named policy owners. It has no plan **by design** — that is the Stage 2 control point in
  §7 working, and `autonomy_tier` is A0 until the conflict closes.
- **`CHG-2026-014904`** cannot proceed because the agent assigned to draft its spec has no
  GitHub AI credits. Issue #6 is open and carries the error.
- **`CHG-2026-014906`** was a Stage 6 anomaly, triaged, and closed as issue #3 on 28 August.
  It will not resume.

What is not legitimate is stopping **silently**. On disk, a deliberate halt and an abandoned
change are the same shape: an intent with nothing after it. Nobody reading the repository,
the chain page, or the gates can tell which they are looking at.

## The reason this matters more than tidiness

§6.2 claims the chain answers *"which production changes in Q2 touched control X, at what
autonomy tier, approved by whom"* in one command. A supervisor's next question is invariably
about the ones that **didn't** ship — what was proposed and abandoned, and on whose authority.
That question currently has no answer in the header, only in a closed issue, a prose banner
one artifact happens to carry, and institutional memory.

Two of these three will resume and one never will, and there is no way to tell them apart.

## Who is affected

- Anyone reading the published chain page, who sees three changes that appear to be mid-flight.
- Anyone auditing what was proposed and not built.
- The next person to write an intent and wonder whether an unfinished chain is a bug.

## Success criteria

1. A chain that stops before a plan declares a terminal state and a reason.
2. `blocked` and `dismissed` are distinguishable — one resumes, one does not.
3. A gate refuses a chain that stops without saying so.
4. The published chain page shows the state.
5. **No fabricated artifacts.** Nothing gets a spec or a plan it does not deserve.

## Out of scope

- Writing the missing specs and plans. `014906` was dismissed and `014904` is waiting on
  credits; manufacturing artifacts for work nobody did would be inventing an audit trail,
  which is worse than the gap being fixed.
- A general workflow state machine. Two terminal values and a reason. Anything richer is
  reimplementing the ITSM this model is explicitly designed to link to rather than replace
  (§6.3).

## Constraints

- No new control objective. This is a header field and a chain rule, and `CHG-04` is
  already the gate for both — a new control would mean editing `policy/`, which floors the
  change at R3 for no gain.

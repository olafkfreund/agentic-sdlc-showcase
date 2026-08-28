---
change_id: CHG-2026-014880
risk_class: R3
autonomy_tier: A2
controls: [CHG-04, TRC-01, HUM-14, TPR-05, SEC-API-01, DP-11, FIN-02, FRZ-01, SOD-01]
data_classification: internal
originator: olaf.krasicki-freund@synechron.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---


# Intent: make the playbook runnable

## Problem

The Agentic SDLC Playbook v1.0 describes a seven-stage lifecycle, five planes, a
portable artifact chain and an autonomy matrix. It is a good document and it is only a
document. When we take it to a bank, the CISO asks "what does the gate actually do when
someone tries that", and the honest answer today is "here is the paragraph about it".

A prospect cannot tell the difference between a control that is designed and a control
that operates. Neither, in the end, can a supervisor.

## Who is affected

Synechron consultants presenting the playbook — every engagement conversation. The
prospect's CISO, head of engineering and internal audit, who need to agree on what "the
agent is allowed to do" means before a programme can start. Our own delivery teams, who
otherwise rebuild this scaffolding per engagement.

## Success criteria

1. A consultant can show a gate **refusing** a change, live, in under a minute.
2. Every claim in the playbook that can be executed, is executed — the Substitution Test
   scores itself from the repository rather than being self-assessed.
3. The repository is built through its own artifact chain. If we exempt ourselves, the
   demo is a lie the audience will notice.
4. Swapping the agent runtime is an edit to one workflow step, not to the operating model.
5. Every generated artifact states plainly that it is a demo.

## Out of scope

- A real model gateway. Routes are declared and the eval runner speaks to a gateway,
  but no gateway is stood up here.
- A real deployment target. The release workflow attests and gates; it deploys to `echo`.
- Anything that would make fabricated evidence look like a real institution's records.

## Constraints

- Must run in a plain GitHub repository with no paid add-on beyond Copilot.
- Must not name a model anywhere, because the Substitution Test checks for it.
- The demo must be reproducible: the same numbers every time it is run.

## Open questions

- Does the target org have the Copilot coding agent enabled? Affects Stages 2, 3 and 5.

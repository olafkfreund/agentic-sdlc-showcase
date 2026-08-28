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

# Spec: two composite adopters, ninety days, cited

## Requirements

### R1 — Composites, labelled, never a named institution

Two illustrative organisations: a tier-1 European bank (~4,000 engineers, second line with
its own reporting line to the board) and an EMI-licensed payments firm (60 engineers, one
compliance lead). Both labelled as composites in the opening table and again in a closing
disclaimer.

The reason is not caution. A fabricated customer reference is the fastest way to lose a
room, and the room this is written for contains people who verify claims for a living.

### R2 — The regulation is real, dated, and linked

| Cited | Why it is the hook |
|---|---|
| EU AI Act Art. 14, binding **2 August 2026** | Requires oversight *technically embedded in the system*, **not merely described in documentation** — which is `policy/autonomy-matrix.yaml` versus a policy PDF, exactly |
| DORA Arts. 28–30, applied **January 2025** | Documented exit strategies; concentration assessed before contracting. This is the Substitution Test's market |
| BCBS 239 | Controls expected to operate *continuously, not only during audit periods* — evidence as a by-product |

Every one carries a link. A claim about a regulation that a reader cannot check is worth
less than no claim, because it invites them to check the others.

### R3 — Sequence, with the reason each step is where it is

Seven steps over ninety days. The load-bearing ordering claims:

- **The autonomy matrix comes first, before any tooling.** The playbook says day one, not
  day sixty, and it is the advice most often ignored. Teams that install tooling first
  spend a quarter retrofitting permissions around decisions engineers already made.
- **The agent arrives at step six.** Steps one to five involve no agent at all, which is
  the argument in structural form: the control layer does not depend on the agent, so the
  agent becomes a productivity decision rather than a governance event.

### R4 — The uncomfortable finding is kept

The control-mapping step is written to produce an awkward result: 34 objectives, nine with
deterministic gates, 25 asserted by a human quarterly. Presented as **the deliverable
rather than a setback**, because a ranked list of which controls are asserted rather than
enforced is more valuable than the framework was asked to produce.

Removing that would make the page a sales document.

### R5 — What differs, and what provably does not

The second organisation gets a diff-level comparison: the autonomy matrix moves up,
CODEOWNERS names a person rather than a fictional team, a GitHub environment replaces a
CAB, and different gates earn their keep. R3-in-production stays A0 in both.

Then the claim that matters, stated as a command rather than a paragraph:

```bash
diff -r meridian/scripts kestrel/scripts     # empty
```

Everything that differs between a tier-1 bank and a sixty-person payments firm lives in
four YAML files. That is the difference between a framework and a template.

## Policy conflicts

**None identified.** Stated explicitly rather than omitted.

Considered: a page aimed at buyers risks drifting into marketing, and marketing is where
verifiable claims go to become adjectives. Mitigated by R2 (everything cited) and R4 (the
unflattering finding stays).

## Verification

| Requirement | Verified by |
|---|---|
| R1 | Composite disclaimer at the top and bottom; no institution named anywhere |
| R2 | Every regulatory claim has a link in the Sources section |
| R3 | Seven steps, each with what/why/produces |
| R4 | The 34-vs-9 finding is present and framed as the deliverable |
| R5 | The comparison table and the `diff` claim are both present |

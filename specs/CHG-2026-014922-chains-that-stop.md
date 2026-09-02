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

# Spec: promote a convention that already exists

## Requirements

### R1 — The field

Two optional §6.2 header fields on the **last** artifact of a chain:

```yaml
status: blocked | dismissed     # absent means active
status_reason: <why, in one line>
```

`blocked` is waiting on a named decision and will resume. `dismissed` was triaged and will
not. Absent means the chain is in progress, so **every existing artifact stays valid** and
nothing needs backfilling.

This is not a new invention. `CHG-2026-014901`'s spec already opens
"**STATUS: BLOCKED ON POLICY CONFLICT**" — the convention existed, in prose, used once,
enforced nowhere and readable by nothing. This makes it a header field so it is queryable
like the rest of §6.2.

### R2 — A reason is mandatory when a status is set

`status` without `status_reason` is the original gap wearing a label. `status_reason`
without `status` is a note nothing can query. Both are rejected.

### R3 — `CHG-04` gains the forward rule

The existing rule looks backwards only. It gains: a chain with no plan must have a terminal
status on its last artifact. It reports `chains_deliberately_stopped` in its evidence, so
"how many proposals were abandoned and why" is answerable from the evidence record rather
than by reading markdown.

No new control objective and no `policy/` edit — `CHG-04` is already the artifact-header
and chain-integrity gate, and this is both. That also keeps the change at R2 and leaves
`substitution_test.py` check 6's control count untouched.

### R4 — The three, stated truthfully

| Change | Stops at | Status | Because |
|---|---|---|---|
| `014901` | spec | `blocked` | policy conflict; named owners must resolve it before engineering sees the spec. A0 until then |
| `014904` | intent | `blocked` | the agent has no GitHub AI credits and cannot start; issue #6 |
| `014906` | intent | `dismissed` | Stage 6 anomaly, triaged, closed as issue #3 on 28 August |

`014901`'s prose banner stays. The header now agrees with it instead of duplicating the
judgement — the banner explains, the field is what a query reads.

### R5 — Visible on the site

The chain index gains a status column, and a stopped chain is labelled where it is listed.
A page that presents a dismissed change identically to one in flight is the same failure in
a different medium.

### R6 — Tested

`scripts/tests/test_artifacts.py`: a status outside the enum is rejected, a status without a
reason is rejected, a reason without a status is rejected, and absent-means-active still
validates.

## Policy conflicts

None. No control objective, risk class, autonomy tier or frozen path changes. R2: nothing
under `policy/` or `.github/workflows/` is touched.

## Verification

- The new rule **fails against the tree before the three headers are set** — run first, in
  that order, so the rule is proven rather than fitted to the answer.
- `make build test lint gates`, `make negative`.
- The published chain page shows all three states.

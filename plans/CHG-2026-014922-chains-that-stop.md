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

# Plan: rule first, then the data

## Files

- `scripts/artifacts.py`
- `scripts/check_artifact_header.py`
- `scripts/tests/test_artifacts.py`
- `docs/artifact-header.md`
- `site/build_pages.py`
- `intent/CHG-2026-014904-agent-invocation-evals.md`
- `intent/CHG-2026-014906-post-deploy-error-rate-anomaly.md`
- `specs/CHG-2026-014901-fx-rounding.md`

## Sequence

1. Read all three before touching any. → verify: **done, and it changed the plan.**
   `014901` looked like an incomplete chain and is a deliberate demonstration of the Stage 2
   control point. Writing it the "missing" plan would have destroyed what it demonstrates.
2. Add `status`/`status_reason` validation to `artifacts.py`.
3. Add the forward rule to `CHG-04`. → verify: **it fails, naming exactly these three and
   nothing else.** Ran before step 4, deliberately.
4. Set the three headers to what is actually true.
5. Tests for the enum, the missing reason, the orphan reason, and absent-means-active.
6. Document the field; render it on the chain index.
7. `make build test lint gates`, `make negative`; push; check the live page.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Fabricating specs and plans to "complete" the chains | **high** — it is the obvious reading of "fix" | Explicitly out of scope. A dismissed anomaly must not grow a plan for work nobody did |
| Destroying 014901's demonstration by completing it | **high, and nearly happened** | Read first. Its spec says BLOCKED ON POLICY CONFLICT; the missing plan is the point |
| Rule written to fit the answer | medium | Rule runs and fails before any header is edited |
| A new control objective, forcing R3 and changing the control count | medium | Extends CHG-04, which already owns chain integrity. `policy/` untouched |
| Existing artifacts invalidated | medium | Absent means active. Nothing needs backfilling |
| `status` becomes a workflow engine | low | Two values and a reason. §6.3 says the ITSM is the system of record |

## Rejected

- **Writing the three missing specs and plans.** Inventing an audit trail for work nobody
  did, which is worse than the gap.
- **A new control objective and gate file.** `policy/` edit, R3 floor, a tenth control in
  `substitution_test.py` check 6 — all to express something CHG-04 already owns.
- **Auto-deriving status from the linked GitHub issue.** Couples the artifact chain to one
  vendor's issue tracker, which Appendix C #11 exists to prevent.
- **A richer lifecycle enum.** §6.3 names the ITSM as the system of record for change state.
- **Removing 014901's prose banner now the field exists.** The banner explains to a reader;
  the field answers a query. They are not duplicates.

## Tests

`scripts/tests/test_artifacts.py`; `make build test lint gates`; `make negative`.

## Rollback

Revert. `status` is optional, so nothing else depends on it.

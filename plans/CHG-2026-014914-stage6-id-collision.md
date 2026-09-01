---
change_id: CHG-2026-014914
risk_class: R3
autonomy_tier: A2
controls: [TRC-01, CHG-04, HUM-14]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---

# Plan: fix the allocator both callers share

## Approach

The reported symptom is one workflow step failing. The cause is a function two callers
share, one of which is a person. Patching the workflow would leave hand allocation broken;
patching the allocator fixes both, and is the smaller diff.

Write the test first, against the current code, so that the diagnosis is proven rather
than assumed.

## Files

- `scripts/draft_intent.py`
- `scripts/tests/test_draft_intent.py`
- `.github/workflows/06-operate.yml`

## Sequence

1. Write `test_draft_intent.py` asserting a reserved-but-unfiled id is skipped.
   → verify: it **fails** against the current allocator. If it passes, the diagnosis is
   wrong and everything below is premature.
2. Add `reserved_change_ids()` reading git refs; union it in `main()`.
   → verify: the test passes; `next_change_id` is still pure.
3. Move the push out of the fallback's way in `06-operate.yml`, and suffix a colliding
   branch name. → verify: `actionlint`/parse clean, and the issue body is honest about a
   failed push.
4. `make build test lint gates`. → verify: green, HUM-14 content with R3/A2.
5. Dispatch Stage 6 and watch it. → verify: completes, and the id it allocates is not one
   any existing branch holds.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| The diagnosis is wrong again | **medium** — it already was once | Step 1 must fail before step 2. A test that passes first time disproves the theory |
| `git ls-remote` unavailable or slow in CI | medium | Failure returns what was found rather than raising; allocation degrades to today's behaviour |
| The fix masks itself tonight | **certain** | Merging 014913 already moved main past the stuck branch. Verification asserts the *mechanism*, not just a green run |
| Declared R2 and refused by HUM-14 | high if careless | Declared R3 for the workflow path floor; A2 is the matrix maximum at R3 in development |
| Suffixing the branch hides a real collision | low | It is a last resort behind R1, and the run number in the name makes it obvious in the branch list |

## Rejected

- **Reading the GitHub issues API for reserved ids.** Needs a token, fails for a person
  working offline, and an id in an issue with no branch collides with nothing.
- **`git push --force`.** It would go green tonight and destroy an untriaged finding.
- **Letting Actions open pull requests.** It would make the fallback unnecessary by
  removing the control the fallback exists to respect.
- **Making the detector idempotent for an ongoing anomaly.** A real problem, genuinely
  separate, and it would hide whether this fix worked.
- **Deleting the stranded `stage6/*` branches.** Untriaged findings. Not a bug fix's call.

## Tests

- `scripts/tests/test_draft_intent.py` — new
- `make build test lint gates`, `make negative`
- Stage 6 dispatched end to end

## Rollback

Revert. The allocator returns to reading the working tree and the nightly returns to
failing on a collision, which is the current state.

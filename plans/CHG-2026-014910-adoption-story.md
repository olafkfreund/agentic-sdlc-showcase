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

# Plan: research first, then write, then cite

## Approach

Research before writing. The temptation is to write the narrative and decorate it with
regulation afterwards, which produces claims shaped to the story. Searching first meant the
AI Act's "technically embedded, not merely described" phrasing — which is the single
strongest line available and describes the autonomy matrix better than the repository's own
documentation does — was found rather than invented.

## Files

- `site/adoption.md`
- `site/index.md`
- `site/story.md`
- `site/_config.yml`

## Sequence

1. Research DORA Arts. 28–30, EU AI Act Art. 14 and supervisory expectations on AI audit
   trails. → verify: each claim traceable to a linked source with a date.
2. Choose two composites far enough apart that a reader locates themselves in one.
   → verify: the same three regulations land on both, differently.
3. Write the ninety-day sequence with the reason each step sits where it does.
   → verify: steps 1–5 require no agent.
4. Write the contrast, ending in the `diff` claim. → verify: the claim is a command.
5. Nav, home card, and a cross-link from `/story/`. → verify: every page 200.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| A composite is read as a real client | **high** — it is the point of writing them well | Labelled at the top and in a closing disclaimer; no institution named |
| A regulatory claim is wrong or stale | high, and it destroys credibility with the exact audience | Every claim researched and linked; dates stated; anything uncitable cut |
| The page becomes marketing | medium | The 34-vs-9 finding stays; every number is one the repository prints |
| It dates as regulation moves | **certain** | Dates are explicit, so it reads as of a moment rather than as timeless |

## Rejected

- **Naming real banks.** More persuasive, and a fabricated customer reference in front of
  an audience that verifies claims for a living.
- **One organisation.** A single tier-1 example tells a sixty-person firm this is not for
  them, which is the opposite of the portability argument.
- **Writing first, citing after.** Produces claims shaped to the narrative. The strongest
  line on the page came out of the research and would not have been invented.

## Tests

- `make gates` and `just site-build`
- Every page returns 200 after deploy
- Each Sources link resolves

## Rollback

Delete the page and its three links. Nothing depends on it.

---
change_id: CHG-2026-014919
risk_class: R1
autonomy_tier: A2
controls: [TRC-01, CHG-04]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-balanced
supersedes: null
---

# Plan: three rules, one stylesheet

## Files

- `site/assets/css/gruvbox.css`

## Sequence

1. `blockquote`: drop the orange stripe, add `--bg0` ground and a 1px `--bg2` edge,
   colour the opening strong. → verify: distinct from a paragraph.
2. `pre`: drop the `--bg3` stripe, keep the 1px `--bg1` edge. → verify: still contained.
3. `.disclaimer`: drop the yellow stripe; the yellow `strong` already carries the caution.
4. → verify: `grep border-left` returns only `.stage`; gates green; hook clean.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| The three boxes become indistinguishable | **medium** — the real risk of removing an accent | Different border weights, different type, coloured leads. R1 is a table, not a hope |
| A blockquote reads as a paragraph | medium | It gains a ground it never had |
| Orange lead over-applies to every bold run | medium | Selector scoped to the first strong of the first paragraph |
| A genuine side-tab slips in later | low | The rule stays armed. Nothing is suppressed |

## Rejected

- **Suppressing the rule file-wide.** The only self-serve option available, and it would
  silence the check for this stylesheet permanently, including on findings that are real.
- **Thinning the stripes to 1px.** Keeps the pattern, keeps the decoration doing the
  content's job, and invites the same flag back at a different threshold.
- **Removing the boxes entirely.** Blockquotes carry the site's callouts; flattening them
  loses a distinction the writing depends on.
- **Touching `.stage`.** A timeline rail, not a card accent, and not flagged.

## Tests

`make build test lint gates`; `grep -n 'border-left\|border-right'`; the design hook.

## Rollback

Revert. Presentation only; nothing depends on it.

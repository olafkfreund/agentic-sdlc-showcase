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

# Spec: move the accent into the typography, and keep the hierarchy

## Requirements

### R1 — Three boxes, three weights

| | Ground | Edge | Distinguished by |
|---|---|---|---|
| `pre` | `--bg0` | 1px `--bg1` | monospace; the quietest, because code already announces itself |
| `blockquote` | `--bg0` | 1px `--bg2` | prose, orange lead |
| `.disclaimer` | `--bg0` | 1px `--bg2` | smaller type, yellow lead |

Code recedes and callouts sit slightly forward of it. That is the inverse of the old
arrangement, where the loudest edge was on the block that needed the least help.

### R2 — The accent moves to the lead, scoped tightly

`blockquote > p:first-child > strong:first-child` takes the orange the border used to. The
selector is deliberately narrow: bold used mid-paragraph stays ordinary bold, so the colour
means "this is the callout's subject" rather than "this text is bold".

`.disclaimer strong` was already yellow. That existing rule is the pattern the other two are
being brought into line with, not a new invention.

### R3 — Blockquote gains a ground

It had none — only the stripe separated it from body text. Removing the stripe without adding
the ground would leave it indistinguishable from a paragraph, which fails R1 of the intent.

## Policy conflicts

None. Presentation only; no control, gate, risk class or frozen path is touched. R1 because
nothing outside `site/` changes and no path floor applies.

## Verification

- No `border-left` or `border-right` remains outside `.stage`.
- `make build test lint gates`.
- The design hook reports no side-tab findings.
- Published pages render with the three boxes still telling themselves apart.

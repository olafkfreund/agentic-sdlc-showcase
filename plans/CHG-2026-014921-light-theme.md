---
change_id: CHG-2026-014921
risk_class: R1
autonomy_tier: A2
controls: [TRC-01, CHG-04]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---

# Plan: resolve in the head, swap tokens, re-render diagrams

## Files

- `site/**`

## Sequence

1. Add the gruvbox light token block under `:root[data-theme="light"]`; keep dark on
   `:root`. → verify: no colour named outside the two blocks and the terminal colours.
2. Inline the resolving script in `<head>` before the stylesheet; `no-js` in the markup.
   → verify: reading the markup, not just the script — this is where the first attempt was
   wrong, adding `no-js` from the script that cannot run when it is needed.
3. Toggle button in the masthead; both glyphs in the DOM, CSS picks one.
4. Toggle script dispatches `themechange`; label updates.
5. Mermaid: store source in `data-src`, re-render on `themechange`, clear
   `data-processed`. → verify: the marker is cleared, or the second render is a no-op.
6. Measure contrast for both palettes; darken only what falls under 4.5:1. → verify: table
   in the spec, computed not estimated.
7. Footer: "Gruvbox dark" is no longer true. → verify: no stale theme name anywhere.
8. `make build test lint gates`; push; check live.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Flash of the wrong theme | **high** if the script is deferred | Inline in `<head>`, before the stylesheet |
| Toggle visible but inert with JS off | **high** — the first attempt had exactly this | `no-js` in the markup, removed by the script |
| Diagrams keep the first theme's colours | high | `data-processed` cleared and source restored before re-running |
| Light accents unreadable on cream | high | Published light palette, then measured; three darkened |
| `localStorage` throws in private mode | medium | try/catch both read and write; the choice degrades to this page only |
| A stale "Gruvbox dark" left in the footer | certain if unchecked | Grepped and corrected |

## Rejected

- **A `prefers-color-scheme` media query in CSS.** Needs the light palette twice.
- **Re-theming the asciinema casts.** A terminal is dark in both themes; recolouring a
  recording misrepresents what was on screen.
- **A tri-state auto/light/dark control.** The first visit already follows the OS. The third
  state costs more explanation than it earns.
- **Inverting the dark accents for light.** Produces a yellow nobody can read on cream.

## Tests

`make build test lint gates`; computed contrast for both palettes; live check.

## Rollback

Revert. Presentation only.

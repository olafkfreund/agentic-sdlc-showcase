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

# Spec: two palettes, each written once

## Requirements

### R1 — Each palette exists exactly once

The stylesheet names no colour except in the two token blocks and the terminal colours at
the foot, so a theme is a token swap and nothing else.

The conventional structure — a `prefers-color-scheme` media query *and* a `[data-theme]`
rule — requires the light palette **twice**, and two copies of a colour set is a future edit
that lands in one of them. This is the duplication CHG-2026-014911 was spent removing.

So the OS preference is resolved in the head script instead, which always stamps an explicit
`data-theme`. The CSS then answers only "dark or light", once each.

### R2 — No flash

The resolving script is inline in `<head>`, before the stylesheet. Deferring it to the end
of the body paints dark and then repaints light, which is the single thing that makes a
theme switch feel broken.

### R3 — Progressive enhancement that is actually correct

`class="no-js"` is in the markup and removed by the script, not added by it. Added by the
script it could never appear when scripts are off — the exact case it exists for — leaving a
toggle that renders and does nothing. With no JavaScript the page is dark, which is the
site's default identity rather than an accident.

### R4 — AA in both themes, measured

Contrast is computed against the grounds each colour actually sits on. Three light values
fall short at canonical gruvbox and are darkened one shade, and only these three:

| Token | Canonical | Shipped | Was | Now |
|---|---|---|---|---|
| `--fg4` / `--gray` | `#7c6f64` | `#796c62` | 4.42:1 | 4.61:1 |
| `--aqua` | `#427b58` | `#38694b` | 3.64:1 | 4.65:1 |
| `--yellow` | `#b57614` | `#966110` | 3.33:1 | 4.61:1 |

All three carry small text — muted metadata, inline code, the current nav item. Palette
fidelity is not worth text somebody cannot read, and a shade is not a redesign. The dark
palette is canonical throughout and needs no adjustment.

### R5 — The diagrams follow

Mermaid bakes resolved colours into an `<svg>`; it cannot be re-themed in place. The
bootstrap keeps each diagram's source in `data-src`, and on a theme change restores the
text, clears mermaid's `data-processed` marker and re-runs. Without clearing that marker
`run()` skips the element and the diagram keeps the theme it was first drawn in.

The light diagram palette is Pertsev's published light accents, not the dark ones lightened —
for the same reason as R4.

### R6 — The switch announces itself

The toggle dispatches a `themechange` event rather than calling the things that care. The
mermaid bootstrap listens; anything added later can listen too, without the toggle growing a
list of dependants.

The control shows the theme it will *give* you, not the one you are in — the page already
tells you where you are by being that colour. Its accessible label updates with it.

## Policy conflicts

None. Presentation only; R1 as nothing outside `site/` changes.

## Verification

- Computed contrast for both palettes across the pairs that carry text.
- `make build test lint gates`.
- Live: `data-theme` stamped before paint; the toggle present; diagrams re-render.

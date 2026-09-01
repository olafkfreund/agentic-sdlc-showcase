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

# Intent: not everyone reads on a dark background

## Problem

The site has one theme. Dark suits the material — it is largely terminal output and code —
and it is a preference, not a universal one. Some readers find light text on dark harder to
read for long stretches; some are in bright rooms; some simply prefer it. The audience this
site is now built for includes board members and risk officers reading an 898-line playbook,
which is a long stretch.

The site also ignores the preference the reader has already expressed to their operating
system, which it can read for free.

## Who is affected

Anyone who prefers or needs a light background, on every page.

## Success criteria

1. A visible control switches themes, and the choice survives navigation and return visits.
2. The OS preference is honoured on a first visit, with the explicit choice overriding it.
3. **No flash of the wrong theme on load.** A switch that flashes reads as broken.
4. Text meets WCAG AA contrast in *both* themes, measured rather than assumed.
5. Everything that draws its own colours — the diagrams especially — follows the switch.
6. Nothing regresses for the existing dark-theme reader.

## Out of scope

- The asciinema recordings. A terminal is dark in both themes because a terminal is dark;
  re-colouring a recording of one would misrepresent what was on screen.
- The favicon and the social card, which are fixed images outside the page's control.
- A third "auto" position on the control. The first visit already follows the OS; a reader
  who has since chosen can clear the choice by clearing site data, and a tri-state toggle
  costs more explanation than it earns.

## Constraints

- No framework and no build step beyond Jekyll, as with everything else in this stylesheet.
- The dark palette stays canonical gruvbox. Any deviation for contrast must be in the light
  palette, minimal, and stated.

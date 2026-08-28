---
change_id: CHG-2026-014907
risk_class: R2
autonomy_tier: A2
controls: [TPR-05, TRC-01, CHG-04]
data_classification: public
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-balanced
supersedes: null
---

# Intent: the demo must run the same way on someone else's machine

## Problem

Everything this repository argues for is verified by running it, and the running
currently depends on whatever happens to be installed on the presenter's laptop. The
README says `python -m venv .venv` and hopes. There is no pinned toolchain, no single
command that performs the demonstration, and no way to find out that an act is broken
except by reaching it in front of the audience.

That is an odd gap in a repository whose thesis is that a control you cannot reproduce
is a control you cannot evidence. A demo whose result depends on the machine is the same
category of claim as a control whose result depends on the reviewer being awake.

There is a second, sharper problem. The demo has an *order*. The gates mean little before
you have seen the loop they guard; the Substitution Test means nothing before you have
seen what would otherwise be lost. Reconstructing that order from memory each time is how
the strongest act — `make negative`, the gates refusing — gets skipped when the meeting
runs late.

## Who is affected

- Whoever presents this, who currently rehearses by remembering.
- Anyone cloning it, whose first impression is a dependency error rather than an argument.
- The maintainer, for whom "does the demo still work" is currently answerable only by
  performing the whole demo.

## Success criteria

1. One command runs the entire demonstration, in order, narrated.
2. It exits non-zero if any act fails, so a broken demo fails in rehearsal rather than in
   front of the audience.
3. The toolchain is pinned and declared, so the demo behaves identically on a machine
   that has never seen this repository.
4. Nothing in the demo is staged, mocked, or replayed from a previous run. Every number
   on screen is computed while the audience watches.
5. The existing `Makefile` remains the single definition of the loop and the gates. CI and
   `AGENTS.md` both point at it, and a second definition would drift.

## Out of scope

- Recording or asciinema capture. Separate concern, separate change.
- Any change to what the gates check, what the evals assert, or what the workflows do.
  This change makes the existing behaviour reproducible; it does not add behaviour.
- Packaging the service for distribution. The payload is deliberately a demo service.

## Constraints

- No new runtime dependency for the repository itself: someone without Nix must still be
  able to `python -m venv .venv && make`.
- The demo must run offline. The act that talks to GitHub is opt-in and degrades to a
  printed note when `gh` is not authenticated.

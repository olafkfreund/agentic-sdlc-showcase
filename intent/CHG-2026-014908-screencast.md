---
change_id: CHG-2026-014908
risk_class: R2
autonomy_tier: A2
controls: [TPR-05, TRC-01, CHG-04]
data_classification: public
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-balanced
supersedes: null
---

# Intent: record the demonstration, so it can be shown without being performed

## Problem

The demonstration exists and is repeatable, but only synchronously: somebody has to be
present, in a terminal, with the toolchain installed. That excludes most of the audience
this repository is for — the reviewer who wants ten minutes on a Friday afternoon, the
person forwarding it to a colleague, the risk function that will not install Nix to
evaluate a control framework.

There is also a gap the local demo cannot close on its own. `just demo` proves the
control layer on a laptop. It does not show the gates reporting as **required status
checks on a real pull request**, or a detector firing with no human in the invocation
path, or a code-owner rule refusing a merge. Those are the claims that matter most to the
audience that asks hardest, and they only exist in CI.

The obvious failure mode is worth naming in advance: a screencast is the easiest artefact
in the world to fake. Re-typing commands into a simulated terminal, or splicing a good
run together from three bad ones, produces something indistinguishable from a recording
of the real thing — to everyone except the person who made it. A repository whose entire
argument is that evidence must be a by-product of the control operating cannot ship a
demonstration that is a reconstruction of one.

## Who is affected

- Anyone evaluating this without a terminal, which is most of the intended audience.
- Whoever presents it, who currently cannot show the CI half at all without switching to
  a browser and narrating over screenshots.
- The maintainer, for whom "is the demo still accurate" and "is the recording still
  accurate" are currently two different questions with two different answers.

## Success criteria

1. One command records the demonstration, repeatably, with no manual editing afterwards.
2. Both halves are recorded: the control layer locally, and the same control layer
   running in CI on a real change.
3. The recording explains what is happening and why, as it happens — not in a caption
   written later.
4. A viewer can jump to a specific act rather than scrubbing.
5. Nothing is re-typed, simulated, spliced, or replayed. Every frame is the run.
6. The recording is playable from the site without a terminal, and readable as text
   without a player.

## Out of scope

- Voice-over or music. The narration is on screen, in the terminal, where it can be read,
  searched and diffed.
- Editing. If a take is wrong the fix is to fix the thing and record again, which is
  cheap precisely because the demo is scripted.
- Recording a browser. The GitHub UI is a rendering of the API, and the API is what the
  controls actually act on.

## Constraints

- The recorder must capture a real session rather than drive a synthetic one.
- The artifact must be diffable. A reviewer should be able to see what changed between
  two recordings without playing either.
- Recording must not require a TTY, so it can run unattended.
- The pipeline recording may trigger only Stage 6, which acts against a fixture and has
  no route to the default branch.

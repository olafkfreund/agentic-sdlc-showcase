---
change_id: CHG-2026-014911
risk_class: R2
autonomy_tier: A2
controls: [TRC-01, CHG-04, TPR-05]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-balanced
supersedes: null
---

# Intent: remove the duplication a whole-repository audit found

## Problem

A repo-wide audit for over-engineering found nine cuts. The largest is the one that will
actually cause a defect: **47 identical lines shared by the two demo scripts** — the colour
setup and the `act`/`say`/`run`/`beat` helpers — copied rather than shared. `beat()` is
byte-identical in both files, which means the next person to change how pausing works
changes it in one and not the other, and nobody notices until a recording pauses in the
middle of a client demo.

The rest is smaller and the same shape: an asciinema player bootstrap pasted into two
pages, four `just` recipes that are bare aliases for `make` with no caller, an
`agent-task` output no workflow consumes, an eighteen-line `contract:` block in
`runtimes.yaml` that no code reads, a `context_file` key declared four times and read
never, and a dead `theme_name`.

None of it is broken. All of it is a second place for a future edit to go missing.

## Who is affected

- Whoever next edits the demo staging and changes one script of two.
- Anyone reading `runtimes.yaml` to learn what a runtime must declare, who cannot tell
  which keys the code reads and which are prose.

## Success criteria

1. The shared demo staging exists once.
2. The player bootstrap exists once.
3. Nothing declared is unread: no dead config keys, no unconsumed outputs, no recipe with
   no caller.
4. Every demo, gate, eval and score behaves identically afterwards. This is a refactor.

## Out of scope

- The eight single-function gate files. `policy/controls.yaml` maps each objective to its
  gate **by filename**; merging them would break the control mapping second line signs.
- The negative suite re-testing what the gates already pass. That redundancy is the thesis.
- `gate.matches()`, which looks like a `fnmatch` reimplementation but is not:
  `PurePath.full_match` is 3.13+ and this targets 3.11+.
- `devenv.nix`. It duplicates the flake's toolchain and is textbook YAGNI unless someone
  runs `devenv shell` — but it was explicitly requested, so it is a decision to revisit
  rather than a cut to make unilaterally.

## Constraints

- Behaviour must not change. A refactor that alters an output is not a refactor.
- Anything with an external caller stays, however alias-shaped. Two audit findings were
  over-called on exactly this point and corrected before any code was cut.

# Review passes

Playbook Stage 5.1. Agent review runs on **every** pull request, identical for all of
them, findings ranked by severity. The passes are defined here rather than in a prompt
someone typed, so they are version-controlled, reviewable, and the same next quarter.

## The three passes

### Pass 1 — Defects and logic errors

Does the code do what the diff claims? Look for: off-by-one and boundary errors,
unhandled error paths, resource leaks, concurrency and check-then-act races, silent
exception swallowing, and behaviour that changes for callers not named in the plan.

### Pass 2 — Security and data protection

Against `.agent/skills/secure-api-review/SKILL.md` and the classification map in
`service/app/models.py`. Look for: missing authentication, unvalidated input, absent
audit events on state change, personal data reaching a log line or an error message,
secrets in the diff, and injection through any content the code reads.

### Pass 3 — Conformance to `spec.md` and `plan.md`

Does the diff implement the spec, and does it match the plan? A file changed that the
plan does not claim is a departure — the fix is to update the plan in the same commit,
not to argue it in a comment. Requirements in the spec with no corresponding code or
test are gaps.

## Severity

The tally is machine-readable and is what any gate reads. The narrative is for humans.

| Severity | Definition | Effect |
|---|---|---|
| **critical** | Exploitable, data-losing, or money-losing as written | Blocks merge |
| **material** | Wrong behaviour, missing control, or a spec requirement unimplemented | Blocks merge |
| **minor** | Correct but fragile; would fail on a plausible near-future input | Author's call, recorded |
| **cosmetic** | Naming, formatting, comment wording | **Capped at 5 per PR** |

The cosmetic cap exists because an unbounded list of nitpicks trains reviewers to skim,
and a skimmed review is worse than no review — it produces the approval without the
attention.

## What the gate does and does not decide

- **Gates on:** the count of `critical` and `material` findings. Deterministic, from the
  tally, in `scripts/review_tally.py`.
- **Never gates on:** the narrative, the tone, or a model's overall verdict. Principle 4
  — no model in the gate. A model that can block a merge is a control whose effectiveness
  you cannot evidence.

Human approval by a code owner is required regardless of the tally. Findings inform;
humans decide.

## The fix loop

A reviewer or the author tags the agent on a comment; the agent addresses it and pushes.
The thread records both the request and the change, which is why the loop runs in the PR
and not in a chat window.

## Feedback into context

**When a review flags the same class of mistake twice, the correction goes into
`AGENTS.md` as part of that review.** Because review reads `AGENTS.md`, the mistake is
caught from the next PR onwards. A repeat finding that never reaches the context file is
a review that will keep finding it forever.

Where the mistake is procedural rather than factual, it goes into the relevant
`SKILL.md`. Where it must always hold, it also gets a gate in `policy/` — write the
policy once as a skill so the agent applies it while working, and once as a gate so the
organisation can prove it held.

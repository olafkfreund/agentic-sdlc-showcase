# Organisation prerequisites

What this repository needs from the GitHub organisation, what it does without, and the
one setting it deliberately declines.

Everything below was established by running the pipeline against
`synechron/agentic-sdlc-showcase`, not by reading documentation.

## Required — nothing works without these

| | Setting | Why |
|---|---|---|
| ✅ | Repository admin for whoever sets it up | Branch protection, environments and required reviewers **are** the deterministic layer. Without admin they become advisory, which inverts the playbook's central claim. |
| ✅ | GitHub Actions enabled | Every gate runs in CI. |

Both are satisfied here. The repository creator is its admin, so org ownership is not
needed.

## Currently unavailable in this org

### Copilot code review

`POST /pulls/{n}/requested_reviewers` with `copilot-pull-request-reviewer[bot]` returns
**HTTP 200 and silently adds no reviewer**. `suggestedActors(capabilities: [CAN_BE_ASSIGNED])`
returns no Bot, so the **Copilot coding agent** is not enabled either.

`05-review.yml` verifies the reviewer actually landed and reports plainly when it did
not. It does not fail the build — a missing advisory layer is not a control failure — but
it does not report success either. **A green check for a control that did not run is
precisely the failure mode this playbook is about.**

*To enable:* Organisation settings → Copilot → Policies → Copilot code review, and
Copilot coding agent.

*Impact while disabled:* Stage 2's automatic spec drafting, Stage 3's agent
implementation and Stage 5's agent review pass all fall back to a human, or to an
`@copilot` mention in the PR by someone with a seat. **The deterministic gates, the
artifact chain, the evidence and the Substitution Test are entirely unaffected** — they
are the control layer and they depend on no agent. That separation is the design working,
not a workaround.

## Deliberately declined

### "Allow GitHub Actions to create and approve pull requests"

Off, and staying off.

It is a **single toggle covering both verbs**. Enabling it so that Stage 6 can open a
pull request would also let a workflow *approve* one — in a repository whose central
claim is that the identity which authored a change cannot approve it.

`06-operate.yml` therefore pushes the branch and opens a triage issue carrying a
one-click compare link. The loop closes identically: the finding is triageable, the
resulting change goes through the normal gate, and the agent still has no route to the
default branch. An organisation that does permit PR creation gets the pull request
instead, with no other change.

This is worth showing a client. The interesting question is never "can the tool do it"
but "what does the tool make you give up in order to do it".

## Configured here

| Setting | Value | Playbook |
|---|---|---|
| Branch protection on `main` | code owner review required; `require_last_push_approval`; linear history; no force push; conversation resolution | Stage 5 control point |
| Required status checks | Deterministic gates · Build, test, lint · Configuration evals · Substitution Test | §5.4 |
| `staging` environment | no reviewers — the agent deploys within a policy envelope | Stage 5.6 |
| `production` environment | required reviewer, `prevent_self_review`, protected branches only | Stage 5.6 |
| `CODEOWNERS` | control layer needs platform team **and** second line | §8.4 SOD-01 |

`require_last_push_approval` is the quiet one that matters: it means an approval is
invalidated by the author pushing again, so an agent cannot collect an approval and then
change the diff underneath it.

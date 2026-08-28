# Organisation prerequisites

What this repository needs from the GitHub organisation, what it does without, and the
one setting it deliberately declines.

Everything below was established by running the pipeline against
`olafkfreund/agentic-sdlc-showcase`, not by reading documentation. Where a row changed
when the repository moved account, the previous finding is kept rather than deleted — a
prerequisite that was once false is the useful half of this page.

## Required — nothing works without these

| | Setting | Why |
|---|---|---|
| ✅ | Repository admin for whoever sets it up | Branch protection, environments and required reviewers **are** the deterministic layer. Without admin they become advisory, which inverts the playbook's central claim. |
| ✅ | GitHub Actions enabled | Every gate runs in CI. |

Both are satisfied here. The repository creator is its admin, so org ownership is not
needed.

## Copilot — available here, and how that is checked

### The coding agent

Available. `suggestedActors(capabilities: [CAN_BE_ASSIGNED])` returns the
`copilot-swe-agent` Bot on this repository, so Stages 2 and 6 hand work to the agent by
**assigning** it — via `.github/actions/assign-copilot`.

The distinction matters more than it looks. `@copilot` in an issue body is a *mention*:
it renders, it notifies nobody in particular, and nothing starts. The coding agent starts
on assignment. A workflow that mentions the agent and reports success is a green check for
a step that did nothing, which is the failure mode this whole playbook is about — so the
action re-reads the assignees after the mutation and warns when the assignment did not
land.

### Where it is not available

The same action degrades honestly: it writes a step summary saying no agent picked the
issue up, emits a `::warning::`, and exits zero. **A missing advisory layer is not a
control failure.** The deterministic gates, the artifact chain, the evidence and the
Substitution Test are entirely unaffected — they are the control layer and they depend on
no agent. That separation is the design working, not a workaround.

*To enable elsewhere:* Settings → Copilot → Coding agent (repository or organisation),
and Copilot code review under Copilot → Policies.

### The default token cannot invoke an agent

Established by running it, not by reading documentation. With the workflow's built-in
`GITHUB_TOKEN`, `suggestedActors(capabilities: [CAN_BE_ASSIGNED])` returns **no Bot at
all** — the same query returns `copilot-swe-agent` under a personal access token with the
`copilot` scope. The assignment therefore resolves to nothing, silently.

This is the third variation on one theme in this repository, and worth naming as a class:
**an API that answers a permission question by returning an empty list rather than an
error.** The CODEOWNERS validator does it, `requested_reviewers` does it, and so does
this. Each one produces a step that succeeds while nothing happened.

`.github/actions/agent-task` therefore takes an optional `agent-token`, and Stages 2 and 6
pass `secrets.AGENT_PAT`. Where the secret is absent it falls back to `GITHUB_TOKEN`, the
assignment finds no bot, and the step **says so** — a plain step summary naming both
causes, plus a `::warning::`. It never reports success.

Configured here, as a fine-grained token scoped to this repository alone:

| Permission | Access | Why |
|---|---|---|
| **Agent tasks** | read and write | Assigning the coding agent. This is the one `GITHUB_TOKEN` lacks. |
| Issues | read and write | Stages 2 and 6 open the labelled task issue |
| Pull requests | read and write | The agent opens its output as a pull request |
| Metadata | read-only | Mandatory, added automatically |

```bash
gh secret set AGENT_PAT --repo <owner>/<repo>    # prompts; never write it to a file
```

Two classic `ghp_` tokens were auto-revoked before this worked, within seconds of being
written to a file on disk. That is GitHub's secret scanning doing its job, and it is worth
knowing before you debug the wrong thing: a token that returns `401` immediately after
creation has probably been revoked, not mistyped.

Without the secret, Stage 2 and Stage 6 open the labelled issue and a human picks it up.
The chain, the gates and the evidence are unaffected.

### The assignee login is not the actor login

The agent is *resolved* as `copilot-swe-agent` and *assigned* as `Copilot`. Both are
declared in `.agent/runtimes.yaml`, because the verification step re-reads the assignees
and has to match the right one. Matching the wrong one — or merely checking the list is
non-empty — passes on an issue assigned only to a human, which is the same silent success
this step exists to refuse.

### Copilot code review

`POST /pulls/{n}/requested_reviewers` with `copilot-pull-request-reviewer[bot]` returns
**HTTP 200 and silently adds no reviewer** where the feature is off. `05-review.yml`
therefore verifies the reviewer actually landed and reports plainly when it did not. It
does not fail the build, and it does not report success either.

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
| `production` environment | required reviewer, protected branches only; **`prevent_self_review` off** | Stage 5.6 |
| `CODEOWNERS` | `@olafkfreund`; on adoption, the control layer needs platform team **and** second line | §8.4 SOD-01 |
| GitHub Pages | built by `pages.yml` with the Jekyll engine, deployed from the `github-pages` environment | — |

### `prevent_self_review` is off here, and must not be in yours

This repository has one maintainer. With `prevent_self_review` on, the only reviewer on
the `production` environment is also the only person who ever pushes, so every release
would sit pending forever — a gate that blocks everything is not a demonstration of a
gate.

It is off, and this line exists so that is a recorded decision rather than an oversight.
**In any real deployment it belongs on**, with a reviewer set that excludes the author and
excludes the agent identity. Segregation of duties still holds structurally here through
CODEOWNERS and `require_last_push_approval`; what is relaxed is the release
authorisation, and only because the population of humans is one.

`require_last_push_approval` is the quiet one that matters: it means an approval is
invalidated by the author pushing again, so an agent cannot collect an approval and then
change the diff underneath it.

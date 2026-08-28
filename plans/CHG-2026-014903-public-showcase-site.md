---
change_id: CHG-2026-014903
risk_class: R3
autonomy_tier: A2
controls: [CHG-04, TRC-01, SOD-01, TPR-05]
data_classification: public
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---

# Plan: publish the showcase and invoke the agent for real

## Approach

Correct the untrue claims before adding anything, so the site is generated from a tree
that already says true things. Then the agent invocation, which is a behaviour change to
the workflows and wants its own verification. The site last, because it is the only part
that cannot break a gate.

The site is generated rather than authored: `site/build_pages.py` reads the chain through
`scripts/artifacts.py`, the same parser the gates use. A hand-copied playbook would be a
second source of truth, and the first thing this repository argues against is a document
that describes a reality it is not connected to.

## Files

- `site/**`
- `.github/workflows/pages.yml`
- `.github/workflows/02-design.yml`
- `.github/workflows/03-gates.yml`
- `.github/workflows/06-operate.yml`
- `.github/actions/assign-copilot/**`
- `scripts/tests/test_readme_claims.py`
- `CODEOWNERS`
- `.gitignore`

## Sequence

1. Repoint `CODEOWNERS` at `@olafkfreund`. → verify: `check_codeowners.py` passes against
   GitHub's validator, not the offline fallback.
2. Correct the README's headline scores and add `test_readme_claims.py`. → verify:
   `make test` green, and the test fails if a number is edited back.
3. Pass `GH_TOKEN` to the CODEOWNERS gate; guard the segregation-of-duties job to
   `pull_request`. → verify: evidence record reports `validator: github`.
4. Add `.github/actions/assign-copilot` and wire it into Stages 2 and 6. → verify: the
   step re-reads assignees and reports honestly on both the available and unavailable
   paths.
5. Add `site/` — config, layouts, Gruvbox stylesheet, four authored pages. → verify:
   Jekyll builds with no external request.
6. Add `site/build_pages.py` and `pages.yml`. → verify: one page per artifact, header
   rendered rather than consumed; the deployed URL serves the site.
7. Re-run everything. → verify: `make build test lint gates`, `make eval`,
   `make substitution` at 12/12, `make negative` at 12 refused.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| The site drifts from the repository it describes | **high** — the default fate of any generated documentation | The playbook and the chain are generated at build time from the files on disk; generated files are git-ignored so no stale copy can be committed |
| An artifact's §6.2 header is silently eaten as Jekyll front matter | high, and invisible when it happens | `build_pages.py` re-emits the header as a fenced YAML block and writes its own front matter |
| The agent assignment appears to succeed while doing nothing | medium — this is exactly how the previous `@copilot` mention failed | The action re-reads the assignees after the mutation and warns when the assignment did not land |
| A public site makes demo evidence look like real audit records | low, high impact | Labelled in the README, the site footer and the index page; the payload is a synthetic service |
| Branch protection makes the repository unusable for a single maintainer | medium | Admins are not forced through the ruleset; segregation of duties remains enforced structurally by CODEOWNERS and the production environment |

## Rejected

- **Building Pages from `docs/` or the repository root.** Either publishes files that are
  not pages, or requires exempting files from the plan-conformance gate to keep it quiet.
  Both trade a real control for a smaller diff.
- **A Jekyll theme gem.** A `Gemfile` and a bundler lock for one stylesheet, in a
  repository that argues about dependency surface.
- **Copying the playbook text into `site/`.** Faster, and wrong for the same reason the
  repository exists.
- **Leaving `docs/org-prerequisites.md` claiming Copilot is unavailable.** It was true of
  the previous organisation and is false here. A stale prerequisite is a claim.

## Tests

- `scripts/tests/test_readme_claims.py` — the headline scores, against the tree
- `make negative` — unchanged, still twelve refusals
- `python site/build_pages.py` — idempotent, page count matches the parsed chain

## Rollback

Disable the Pages deployment and revert the commit. The site is generated, so nothing
downstream holds state. The workflow changes are additive: reverting them returns the
agent steps to a mention, which is where they were.

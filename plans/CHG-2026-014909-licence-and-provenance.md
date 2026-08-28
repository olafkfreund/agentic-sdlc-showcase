---
change_id: CHG-2026-014909
risk_class: R3
autonomy_tier: A2
controls: [TPR-05, CHG-04, TRC-01]
data_classification: public
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-balanced
supersedes: null
---

# Plan: licence it, de-brand it, re-record what recorded the old name

## Approach

Licence first, because it is the blocker; then provenance; then re-record. The rename is
a `git mv` so the history follows the file, and the only code change is the one path
`site/build_pages.py` reads.

The re-record is sequenced last deliberately: the cast has to capture the tree as it
finishes, and any earlier take would show the old name.

## Files

- `LICENSE`
- `NOTICE`
- `SECURITY.md`
- `CONTRIBUTING.md`
- `Agentic-SDLC-Playbook.md`
- `pyproject.toml`
- `AGENTS.md`
- `site/**`
- `.github/workflows/05-release.yml`

## Risk class

Declared R2 on first draft and **refused by `HUM-14`**: the change claims
`.github/workflows/05-release.yml`, and `policy/risk-classes.yaml` floors anything
touching the control layer at R3. Raised to R3, which the autonomy matrix caps at A2 in
development — unchanged from what this change was already running at.

Recorded rather than silently corrected, because a risk class that moves to make a gate
quiet is exactly what the path floors exist to catch, and the fact that it caught its own
author is worth more than a tidy artifact.

## Sequence

1. Fetch the canonical Apache-2.0 text; fill the appendix placeholders. → verify: GitHub
   reports the licence as `Apache-2.0`; no `[yyyy]` remains.
2. `NOTICE` stating plainly what may be done, and why the licence choice matters here.
   → verify: it answers "may I fork this commercially" without a lawyer.
3. `SECURITY.md` and `CONTRIBUTING.md`. → verify: GitHub's community profile lists both.
4. `git mv` the playbook; strip the byline, the section heading, the §6.2 annotation and
   the closing line. → verify: no case-insensitive match in the tree.
5. Repoint `site/build_pages.py`, `pyproject.toml`, `AGENTS.md`, the README and the
   attestation predicate. → verify: `just site-build` regenerates `/playbook/`.
6. Re-record `control-layer.cast`. → verify: the cast no longer contains the old address,
   and it was regenerated rather than edited.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| The licence is typed from memory and is subtly not Apache-2.0 | medium, and invisible | Fetched from `apache.org` over TLS; GitHub's own detector confirms the SPDX id |
| A recorded cast is edited rather than re-recorded, to save time | **high** — it is one `sed` away | Named as forgery in the spec; `just record local` regenerates it in under a minute |
| De-branding is mistaken for a transfer of authorship | medium | The intent records that removing a byline changes attribution, not authorship, and that relicensing assumes an entitlement held outside this repository |
| The playbook rename breaks the generated site page | medium | One path in `site/build_pages.py`; verified by regenerating |
| `SECURITY.md` invites noise about the synthetic service | medium | Out-of-scope section says plainly that `service/` is a fixture |

## Rejected

- **MIT.** Shorter, and leaves the patent position implicit — the first thing an
  enterprise legal review asks about.
- **Editing the cast with `sed`.** One command, and it would make the recording a
  reconstruction that is textually indistinguishable from a real one. The repository
  rejected `vhs` for precisely this; rejecting it again here costs a minute.
- **A generic `CONTRIBUTING.md`.** It would tell contributors to open a pull request with
  a good description, which the plan-conformance gate would refuse.
- **Leaving the playbook unlicensed alongside a licensed implementation.** Two sets of
  terms in one repository is the ambiguity this change exists to remove.

## Tests

- `make build test lint gates` and `make negative`
- `just demo-fast` — exit zero
- `grep -ri` for the vendor name across the tree — no match

## Rollback

Revert the commit. The rename is tracked, so history follows the file.

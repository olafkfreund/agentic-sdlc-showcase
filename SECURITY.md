# Security policy

## Reporting a vulnerability

Report privately through GitHub's **[Report a vulnerability](https://github.com/olafkfreund/agentic-sdlc-showcase/security/advisories/new)**
form. Please do not open a public issue for anything exploitable.

Expect an acknowledgement within three working days.

## What this repository is, and what that means for scope

This is a **reference implementation with a synthetic payload**. `service/` exists so the
deterministic gates have real code to pass or fail on; it is not a production payments
service, it processes no real data, and it is deployed nowhere.

**In scope** — and genuinely useful to report:

- A gate that can be made to pass on a change it should refuse. This is the one that
  matters: the repository's whole claim is that `scripts/check_*.py` cannot be talked
  past, and a bypass is a defect in the argument, not just in the code.
- A way for the agent identity to reach the default branch, approve its own change, or
  exceed the tier `policy/autonomy-matrix.yaml` permits.
- Anything that would let workflow content, issue text or dependency documentation be
  executed as instruction rather than read as data.
- Secrets, tokens or personal data committed to the tree or reachable from a workflow.
- A supply-chain weakness in the workflows: an unpinned action, an over-scoped token, a
  privileged trigger on untrusted input.

**Out of scope**, and stated so nobody wastes their time:

- Findings against `service/` treated as if it were a production service — missing rate
  limiting, no TLS, an in-memory store. It is a fixture.
- The synthetic evidence records and change ids. They are demo output, labelled as such.
- `gateway/*` routes in `.agent/routes.yaml` pointing at `*.internal.example.com`. There
  is deliberately no live gateway.

## What this repository will not do

It will not enable *"Allow GitHub Actions to create and approve pull requests"*. That is a
single toggle covering both verbs, and this repository will not trade segregation of
duties for convenience. See `docs/org-prerequisites.md`.

Where a control here is weaker than it looks, that is recorded rather than hidden —
`enforce_admins` and `prevent_self_review` are both off for a single-maintainer
repository, and both are documented with the reason and the caveat that neither should be
off in a real deployment.

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

# Intent: make the repository legally takeable, and unambiguous about whose it is

## Problem

The repository is public, complete, and about to be sent to customers. It has **no
licence**, which in most jurisdictions means all rights reserved.

Meanwhile the README contains an *"Adopting this"* section that instructs the reader to
fork it, rewrite `policy/controls.yaml` against their own control library, replace the
teams in `CODEOWNERS`, and swap out `service/`. Every one of those instructions is an
invitation the licence does not permit anyone to accept. In the regulated-finance audience
this is written for, that gap is not theoretical: the legal review happens before the
technical one.

There is a sharper version of the problem, and it is the one this repository should be
least comfortable with. Its central argument is that an operating model must be
**portable** — that you can change your mind about a vendor without rebuilding your
controls. It scores itself 12/12 on exactly that. But portability is a claim about what
you are permitted to take, not only about what you are technically able to lift. A
repository that argues for portability while being legally untakeable has a gap between
what it demonstrates and what it delivers, and that gap is the same shape as every defect
the gates exist to catch.

The second problem is provenance. The playbook document carried a corporate byline while
the repository lives on a personal account, and a corporate email address appeared as the
`originator` in the seeded chain. A reader receiving this could not tell from the
repository alone whose work it is or under what terms it arrives — three questions
(is this sanctioned, whose is it, may I use it) that should be answered before they are
asked.

## Who is affected

- Anyone who takes the README at its word and forks this.
- The legal or procurement function that reviews it before an engineering team is allowed
  to look, and currently finds nothing to review.
- The author, whose position is currently implicit where it should be stated.

## Success criteria

1. A licence that permits commercial adoption and adaptation, chosen for what an
   enterprise legal review actually asks about rather than for brevity.
2. Attribution and terms unambiguous from the repository alone, with no external context
   required.
3. A security reporting route, with a scope that says plainly which findings are useful
   and which are wasted effort against a synthetic fixture.
4. A contribution guide that reflects the process this repository demonstrates, rather
   than a generic one that would contradict it.
5. No corporate branding anywhere in the tree.
6. Every gate still passes; the demo still runs; nothing about the argument changes.

## Out of scope

- Rewriting the playbook's substance. Only its byline and section headings change.
- A trademark or a code of conduct. Neither is load-bearing at this size.
- Re-licensing anything downstream. There are no dependents.

## Constraints

- The licence text must be the canonical one, fetched rather than typed from memory.
- Removing a byline changes attribution, not authorship. This change assumes the author
  is entitled to relicense the material it covers.
- Historical artifacts in the chain may have their originator corrected, but recorded
  screencasts must be **re-recorded** rather than edited. A cast that has been altered
  after the fact is a forgery, whatever the reason for the edit.

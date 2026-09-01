---
change_id: CHG-2026-014918
risk_class: R2
autonomy_tier: A2
controls: [TRC-01, CHG-04]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---

# Intent: the playbook, for people who will not read it

## Problem

The playbook is now 898 lines. v1.1 added a plain-terms front page, a glossary and a line of
plain English under every heading precisely because half its intended audience — board
members, business sponsors, risk officers without an engineering background — were bouncing
off §5 and never reaching §6.

Readability was the right fix and it does not reach everyone. Some of the audience will not
read a long document in any register, and will listen to a twenty-six minute conversation on
a commute.

A Google NotebookLM audio overview of the playbook exists. It is currently a 50 MB file in
the repository root, tracked by nothing, claimed by no plan, and refused by TRC-01 — which
is how it was noticed.

## Who is affected

- The reader who would engage with this material but not in this format.
- Anyone cloning the repository, who pays for however this file is stored, permanently.

## Success criteria

1. The audio plays from the site, without a download and without leaving the page.
2. It is discoverable: named in the navigation, on the home page and in the README.
3. It is honestly labelled as AI-generated narration derived from the playbook, not as
   authored commentary, and the playbook stays the source of truth.
4. The repository does not carry four times more bytes than the content needs.

## Out of scope

- A transcript. Worth having for accessibility and search, and it is a separate piece of
  work with its own verification — a generated transcript nobody has checked against the
  audio is a second source of truth that disagrees with the first.
- Playback that survives navigating between pages. This is a static multi-page site; audio
  stops on navigation. Making it persist means client-side routing, which is a large change
  to a small site for a small benefit.

## Constraints

- **Git LFS is not an option.** GitHub Pages does not resolve LFS objects; it would serve the
  pointer file and playback would break. The audio has to be a real file in the repository,
  and therefore in its history permanently.
- Whatever ships is permanent. That makes the encoding decision worth making once, properly.

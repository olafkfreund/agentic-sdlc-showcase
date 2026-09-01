---
change_id: CHG-2026-014920
risk_class: R1
autonomy_tier: A2
controls: [TRC-01, CHG-04]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---

# Intent: a way into the argument that takes ten seconds

## Problem

The front page currently opens with a sixteen-second terminal recording. That is excellent
for an engineer and it presumes the visitor already knows what they are looking at. Someone
arriving cold gets gates refusing before they know what a gate is or why one should refuse.

A hand-drawn overview of the whole argument exists — the governance shift, the Substitution
Test, the J-curve, the artifact chain, the autonomy matrix — on one image. It is currently a
5.8 MB PNG in the repository root, tracked by nothing.

This is the same audience gap v1.1 and the audio overview both addressed, in a third
register: the reader who will neither read 898 lines nor listen for twenty-six minutes, but
will look at a picture.

## Who is affected

- The visitor who lands on the front page and leaves before understanding what this is.
- Anyone cloning the repository, who pays for however the image is stored, permanently.

## Success criteria

1. It is the first thing on the front page, above the recording.
2. It is legible on a phone and zoomable to full resolution.
3. Its provenance is stated: AI-generated, from the playbook, not authored analysis.
4. **Where it disagrees with the playbook, the page says so.**
5. The repository does not carry an order of magnitude more bytes than the page needs.

## The disagreement, which is the interesting part

The graphic is titled "Mapping the three planes of architecture" and lists Model Access,
Context and Control. **§5 of the playbook has five planes.** Agent Runtime and Evidence are
absent — and Evidence is a strange one to lose from a graphic whose own caption reads
"evidence is a by-product".

This repository's entire argument is that published material must not drift from its source.
Shipping "three planes" beside a playbook that says five, without comment, would be a small
instance of exactly the failure the document is about. The options were to not publish it, to
edit it, or to publish it with the gap named. The third is the honest one: the graphic is
good, the omission is real, and a reader who notices the discrepancy should find that we
noticed first.

## Out of scope

- Regenerating or editing the image to say five. It is a generated artefact with a stated
  provenance; retouching it to agree with the source would make its provenance a lie.
- Using it as the social preview card. That is a separate decision with its own crop and
  aspect ratio.

## Constraints

- Whatever ships is in git history permanently, as with the audio under CHG-2026-014918.

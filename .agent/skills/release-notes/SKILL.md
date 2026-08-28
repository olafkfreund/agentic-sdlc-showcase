---
name: release-notes
description: Generate the release record for a deployment. Use when preparing a release
  or when the pipeline requests a release note for a merged change.
version: 1.0.0
policy_owner: Head of Release Management
control: CHG-04
stage: 5
---

# Release notes

The release record is an artifact in the chain, not a changelog. It must let someone
reconstruct, months later, what was deployed and under whose authority.

Include, for each change in the release:

- `change_id`, and the ITSM record it links to
- the artifact digest deployed, not a tag — tags move
- risk class and the autonomy tier the change actually ran at
- the gates that ran and their results, by control id
- the named approver for the production environment
- the rollback command, verbatim, tested

Group by risk class, R3 first. A reader scanning for what could hurt them should not
have to read past the first section.

Write in plain past tense about what changed for a user. "Refunds can now be issued
against a settled payment" — not "implemented `POST /refunds` endpoint". The engineering
detail is in the diff; the release record is for the people who did not read it.

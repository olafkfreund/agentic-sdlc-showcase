---
change_id: CHG-2026-014916
risk_class: R3
autonomy_tier: A2
controls: [TRC-01, CHG-04, HUM-14]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---

# Spec: ask whether it is already tracked, in detection, once

## Requirements

### R1 — The question belongs to `detect`, not to either consumer

`diagnose` and `propose` both raise findings, so putting the lookup in each is the same
six lines twice — the duplication `CHG-2026-014911` was spent removing, reintroduced in
YAML where no linter will find it.

"Is this finding new?" is part of detection. `detect` runs first, holds the metric, and
gains one output, `existing_finding`: the number of an open Stage 6 issue already tracking
this metric, or empty. Both downstream jobs gate on it in their existing `if:`.

The metric name is added to `detect_anomaly.py`'s `GITHUB_OUTPUT` block. It already
computes it — `result["metric"]` — and merely does not emit it.

### R2 — Matching is deterministic and narrow

An open issue matches when it carries the `stage-6` label and its title contains the
metric name. Both proposing paths already title their issues with it.

Deliberately narrow. Title-and-label is inspectable, needs no state, and is wrong in only
one direction: an unusual title produces a duplicate, which is today's behaviour. Anything
cleverer — similarity scoring, a model judging sameness — puts a judgement call in
detection, which principle 4 forbids.

### R3 — Fails open, and says which way it failed

If the lookup errors or the API is unavailable, `existing_finding` is empty and the
finding is raised. A duplicate is an annoyance; a suppressed real anomaly is worse than the
problem being fixed.

### R4 — Suppression is visible or it is not suppression

A run that suppresses writes to its step summary which issue it deferred to. A silent skip
is indistinguishable from a detector that stopped working — the failure that cost three
nights under `CHG-2026-014914`.

### R5 — Closing a finding re-arms the detector

Matching is on **open** issues only. Close the finding and the next breach raises a new one.
This is what stops suppression becoming permanent silence, and it makes closing an issue the
explicit act of saying "tell me again if this recurs".

## Policy conflicts

None. `.github/workflows/` floors this at **R3** (`policy/risk-classes.yaml`), so it is
declared R3/A2 — the matrix maximum at R3 in development.

The `detect` job gains `issues: read`. It does not gain `issues: write`: detection
looks, and the jobs that were already permitted to write are the ones that write.

## Verification

- `make build test lint gates`.
- `scripts/tests/test_detect_anomaly.py` extended: the metric is emitted to
  `GITHUB_OUTPUT`.
- Dispatch with the tracked finding open → suppressed, summary names the issue.
- Close it, dispatch again → a new finding is raised. R5 is the requirement most likely to
  rot, so it gets tested by doing it.

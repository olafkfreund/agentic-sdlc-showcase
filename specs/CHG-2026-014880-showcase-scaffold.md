---
change_id: CHG-2026-014880
risk_class: R3
autonomy_tier: A2
controls: [CHG-04, TRC-01, HUM-14, TPR-05, SEC-API-01, DP-11, FIN-02, FRZ-01, SOD-01]
data_classification: internal
originator: olaf@freundcloud.com
agent_identity: svc-agent-platform
model_route: gateway/tier-frontier
supersedes: null
---


# Spec: a runnable reference implementation

## Summary

A repository implementing all seven stages of the playbook against a deliberately small
payments service, with GitHub Copilot as the agent runtime and every portable asset in
`AGENTS.md` / `SKILL.md` / MCP / OTel form.

## Requirements

| # | Requirement | Traces to |
|---|---|---|
| R1 | A payload service carrying real, gateable policies | Success criterion 1 |
| R2 | Deterministic gates that fail on a bad change, with negative tests proving it | Success criterion 1 |
| R3 | Appendix C executed against the repository, scored 12/12 | Success criterion 2 |
| R4 | The repository's own scaffolding passes its own chain and gates | Success criterion 3 |
| R5 | Copilot invoked in exactly one step per stage, replaceable in isolation | Success criterion 4 |
| R6 | Every generated evidence artifact labelled as demo output | Success criterion 5 |
| R7 | An eval suite of 20-50 cases with a non-interactive runner | Playbook Stage 4.5 |
| R8 | Stage 6 detection deterministic and unit-tested | Playbook Stage 6.2 |

## Design

Seven workflows, one per stage, plus a shared composite action for setup. The gates are
Python scripts reading version-controlled YAML policy; each writes a JSON evidence record
as a by-product of running.

**Rejected: Rego and Conftest for the governance rules.** The playbook names OPA/Rego as
an example of a deterministic mechanism, and a bank audience recognises it. But encoding
the autonomy matrix in both Rego and Python means two homes for one rule, and the two
will drift — at which point the control is worse than either alone. The control
requirement is "a deterministic enforcement point outside the agent", which Python over
YAML satisfies. Conftest is documented as the swap-in for estates standardised on OPA,
where it would replace the Python rather than duplicate it.

**Rejected: a larger, more realistic service.** Every line of payload is a line that is
not a control. The service exists to give the gates something to refuse.

## Data

No personal data. The payments service handles synthetic payloads only; `models.py`
classifies fields as `personal` so the classification machinery has something to protect,
and the test fixtures use obviously fictional values.

## Policy conflicts

None identified. This repository has no production deployment, no real customer data and
no regulatory reporting obligation of its own.

One point worth recording rather than flagging: the evidence artifacts this repository
produces are **fabricated demo output**. They are labelled as such in the README, in
`scripts/query_evidence.py` output, and in the evidence bundle. Presenting them as a real
institution's audit records would be misrepresentation, and the labelling is what keeps
that from happening by accident.

## Non-functional

The full loop (`make build test lint gates eval`) must complete in under 60 seconds on a
laptop, or nobody will run it before pushing.

## Test strategy

Positive: `make build test lint gates eval` green. Negative: a scripted branch per gate
that must go red — this is the real proof, since a gate that has never refused anything
is indistinguishable from a gate that cannot.

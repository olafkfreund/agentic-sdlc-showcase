# The artifact header

Playbook §6.2. Every artifact in the chain (`intent/`, `specs/`, `plans/`) opens with
this YAML header. It is what makes the chain queryable rather than merely present.

```yaml
---
change_id: CHG-2026-014882          # links to the system of record
risk_class: R2                      # R1 routine | R2 standard | R3 material (§8.1)
autonomy_tier: A2                   # A0-A3 (§8.2), within the matrix (§8.3)
controls: [SEC-API-01, CHG-04, DP-11]   # control objectives in scope (policy/controls.yaml)
data_classification: internal       # public|internal|confidential|personal|restricted
originator: j.ortiz@example.com
agent_identity: svc-agent-platform  # machine identity, NOT the human
model_route: gateway/tier-frontier  # a route, never a raw model name
supersedes: null
---
```

## Why each field is there

| Field | What it buys you |
|---|---|
| `change_id` | Joins the repository artifact to the ITSM record. Without it the chain is an island. |
| `risk_class` | Selects the row of the autonomy matrix. Raised automatically by `policy/risk-classes.yaml::path_floors` if the paths touched demand it — a change cannot self-declare its way past a gate. |
| `autonomy_tier` | What the agent was permitted to do. Checked against the matrix by `scripts/check_autonomy.py`. |
| `controls` | Which control objectives this change is in scope for. This is the field that answers "which changes touched SEC-API-01 last quarter". |
| `data_classification` | Routes the work. `personal` binds to `gateway/tier-sovereign`. |
| `originator` | A named human. Accountability stays with people (principle 7). |
| `agent_identity` | Distinct from the human, in every log and every record (Substitution Test #9). Segregation of duties depends on it. |
| `model_route` | A route, not a model. Enforced by regex in `scripts/artifacts.py`. This is what lets you change model on a Monday. |
| `supersedes` | The prior artifact this replaces, so amendments are traceable. |

## The question this answers

> Which production changes in Q2 touched control SEC-API-01, which of them were
> agent-authored, at what autonomy tier, and who approved each one?

`python scripts/query_evidence.py --control SEC-API-01 --quarter 2026Q2`

Minutes rather than a week. Per the playbook, that is the single highest-value output
of the whole programme.

## Optional fields

| Field | Use |
|---|---|
| `frozen_path_exception` | List of frozen paths this change is permitted to touch. Requires R3 and architect approval (`policy/frozen-paths.yaml`). |
| `itsm_record` | Direct URL to the ServiceNow/Jira record, where the ID alone is not enough. |
| `incident_id` | Set when this change originates from an incident (Stage 6). |

## Terminal status — when a chain stops

Chains stop, legitimately and often: a policy conflict second line must resolve, an anomaly
triaged as noise, work waiting on something outside the repository. Two optional fields say
so, on the **last artifact of the chain**:

```yaml
status: blocked          # waiting on a named decision — will resume
status_reason: >-
  Two policy conflicts cannot be jointly satisfied; named owners resolve them
  before engineering sees this spec. autonomy_tier stays A0 until they close.
```

| Value | Means |
|---|---|
| absent | active — the chain is in progress |
| `blocked` | stopped on something outside this chain, and **will** resume |
| `dismissed` | triaged, and will **not** resume |

`status_reason` is mandatory whenever `status` is set, and rejected when it is not.
`status: blocked` with no reason is the gap it exists to close, wearing a label.

**Why the field exists.** `check_artifact_header.py` enforced the chain backwards only — a
plan implies a spec implies an intent — so an intent that never became a spec passed
silently, forever. On disk a deliberate halt and an abandoned change were the same shape:
nothing after the last artifact. Three chains in this repository were in that state, and
nobody reading the repository, the published chain page or the gates could tell which was
which. Two of the three will resume; one never will.

The gate now refuses a chain that stops short of a plan without declaring a status, and
reports `chains_deliberately_stopped` in its evidence — so "what was proposed and abandoned,
and on whose authority" is answerable from the evidence record rather than from memory.

Absent means active, so every artifact written before this field existed remains valid.

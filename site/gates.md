---
layout: page
title: The gates that refuse
permalink: /gates/
lede: >-
  Twelve deliberate violations, one per protected thing, each proven to go red.
  A gate verified only by passing is indistinguishable from a gate that cannot fail.
---

## Run it yourself

```bash
make negative
```

The script breaks the thing each gate protects, asserts the gate refuses, and restores
the tree. It refuses to run on a dirty working tree, because it edits files.

```
Negative tests — each gate must refuse:

  refused         FIN-02  float on a monetary field
  refused         DP-11   personal data in an error message
  refused         DP-11   logging outside audit.safe_log()
  refused         SEC-API-01  unauthenticated, unaudited POST
  refused         FRZ-01  edit to a frozen path
  refused         SOD-01  CODEOWNERS rule guarding a missing path
  refused         SOD-01  control layer with no named owner
  refused         CHG-04  artifact with no header
  refused         CHG-04  raw model name instead of a route
  refused         HUM-14  R3 change claiming A3 autonomy
  refused         HUM-14  material change declared R1
  refused         TRC-01  code changed with no plan claiming it

  12 refused, 0 did not.
```

## What each gate decides

| Control | Gate | Refuses |
|---|---|---|
| `FIN-02` | `check_money.py` | A `float` or a `round()` anywhere near a monetary value. Money is `Decimal`, or it is a rounding error waiting for volume. |
| `DP-11` | `check_pii.py` | A field classified `personal` reaching a log line or an error message, and any logging outside `audit.safe_log()`. |
| `SEC-API-01` | `check_endpoints.sh` | A state-changing route with no authentication, no audit event, or an untyped body. |
| `FRZ-01` | `check_frozen_paths.py` | An edit to a frozen path without a recorded exception at R3 with architect approval. |
| `SOD-01` | `check_codeowners.py` | A CODEOWNERS rule GitHub would silently ignore, and any part of the control layer left to the catch-all. |
| `CHG-04` | `check_artifact_header.py` | An artifact with no §6.2 header, a malformed one, a raw model name where a route belongs, or a gap in the chain. |
| `HUM-14` | `check_autonomy.py` | An autonomy tier above what the matrix permits for the risk class — including a material change self-declaring as routine. |
| `TRC-01` | `check_plan_conformance.py` | A code file in the diff that no plan's `## Files` section claims. |

## The two things that make these gates unusual

### They call GitHub's own validator

A CODEOWNERS rule whose owner does not exist is **silently ignored**. The rule stays in
the file, branch protection still says *require review from Code Owners*, and the
requirement is satisfied by nobody. That is a control which reads as operating while it
is not — precisely the failure mode this repository is about. So the gate asks GitHub,
rather than trusting the file.

### The risk class comes from the paths, not the header

```yaml
path_floors:
  - { pattern: "service/app/money.py",  min_class: R3, reason: "monetary logic" }
  - { pattern: "service/app/audit.py",  min_class: R3, reason: "audit and PII controls" }
  - { pattern: "service/app/models.py", min_class: R3, reason: "data classification map" }
  - { pattern: "policy/**",             min_class: R3, reason: "control layer" }
  - { pattern: ".github/workflows/**",  min_class: R3, reason: "control layer" }
```

A change that touches the classification map is material whatever its header says. You
cannot self-declare your way past a gate.

## No model in the gate

> Models diagnose, propose, draft and review. The decision to allow or block is
> arithmetic over policy that lives in `policy/` as version-controlled YAML — the same
> tables governance signed off.

A model that can block a merge is a control whose effectiveness you cannot evidence. Ask
what its false-negative rate was last quarter and there is no answer, because there is no
stable artefact to have measured. Arithmetic over a YAML table has an answer, and the
table is reviewable by people who do not read Python.

Every gate writes a JSON record to `evidence/` as it runs — control id, result, findings,
commit, actor, timestamp. Evidence is a by-product of the control operating, never a
reconstruction exercise at audit time.

```bash
python scripts/query_evidence.py --control SEC-API-01
```

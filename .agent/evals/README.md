# Eval suite

Playbook Stage 4.5. Twenty-odd real tasks with accepted outcomes, each reduced to a
prompt plus the checks that define acceptable.

**Why this matters more here than anywhere else.** In a vendor-neutral design the model
is a routed dependency that *will* change. This suite is the mechanism that lets you
change it deliberately: swap the route in a branch, run the suite, compare the pass
rate, decide. Without it, model substitution is a leap of faith and the Substitution
Test is unpassable in practice however portable the file formats are.

## Two modes

| Mode | What it checks | Needs a gateway |
|---|---|---|
| `--mode static` (default) | The **configuration** each case depends on is present and correct. If someone deletes the decimal-money rule from `AGENTS.md`, the eval that relies on it fails. | no |
| `--mode gateway` | Sends each prompt through `.agent/routes.yaml` and applies the checks to the response. This is the mode that qualifies a new model. | yes |

CI runs `static` on every change to `AGENTS.md`, `.agent/**`, `policy/**` or `scripts/**`
and gates the merge on the pass rate. `gateway` runs on the quarterly route review and
whenever a route binding changes.

## Adding a case

Copy any file in `cases/`. Every production incident becomes a permanent eval, written
by the team that owned it (Stage 4.6) — set `origin: incident:<id>` so the ledger shows
the loop closing.

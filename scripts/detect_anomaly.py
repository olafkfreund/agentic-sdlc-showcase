#!/usr/bin/env python3
"""Stage 6 detection. Deterministic, version-controlled, unit-tested.

**No model in detection** (playbook Stage 6.2). This script decides the tier; the
agent is only invoked afterwards, at the autonomy the tier permits, and only ever
writes through the normal PR gate.

Western Electric rules catch drift as well as spikes — a metric that walks away from
its baseline over a fortnight never trips a simple threshold and is usually the more
expensive problem.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import gate  # noqa: E402

TIER_ORDER = ["none", "1sigma", "2sigma", "3sigma"]


def baseline(history: list[float]) -> tuple[float, float]:
    """Mean and standard deviation of the baseline window."""
    if len(history) < 2:
        raise ValueError("baseline needs at least two observations")
    return statistics.fmean(history), statistics.stdev(history)


def sigmas(value: float, mean: float, sd: float) -> float:
    """Signed distance from the mean, in standard deviations."""
    return 0.0 if sd == 0 else (value - mean) / sd


def first_breach(z: list[float], threshold: float = 2.0) -> int | None:
    """Index of the first observation that leaves the band, or None."""
    return next((i for i, x in enumerate(z) if abs(x) > threshold), None)


def correlate(z: list[float], deploys: list[dict]) -> dict | None:
    """Which deploy was live when the breach began.

    The last marker at or *before* the first breaching observation — never the
    nearest. A deploy that landed after the excursion started did not cause it, and
    blaming it sends triage to the wrong team, which is worse than naming nobody.

    Returns None when there is no breach or no marker in the window. It does not
    raise: a detector that can fail is a detector that gets switched off, and this
    is a convenience riding along with the signal, not the signal.
    """
    onset = first_breach(z)
    if onset is None or not deploys:
        return None
    prior = [d for d in deploys if d.get("index") is not None and d["index"] <= onset]
    if not prior:
        return None
    suspect = max(prior, key=lambda d: d["index"])
    return {**suspect, "onset_index": onset, "observations_before_breach": onset}


def evaluate(history: list[float], recent: list[float], deploys: list[dict] | None = None) -> dict:
    """Apply the Western Electric rules to `recent` against `history`'s baseline.

    Returns the highest tier any rule fires at, and which rules fired. Both halves
    matter: the tier drives the action, the rule names go in the intent so a human
    triaging the queue knows what kind of problem this is.
    """
    mean, sd = baseline(history)
    z = [sigmas(v, mean, sd) for v in recent]
    fired: list[str] = []

    # Rule 1 — one point beyond 3 sigma. A spike.
    if any(abs(x) > 3 for x in z):
        fired.append("rule_1: one point beyond 3 sigma")

    # Rule 2 — two of three consecutive beyond 2 sigma, same side.
    for i in range(len(z) - 2):
        window = z[i : i + 3]
        for side in (1, -1):
            if sum(1 for x in window if x * side > 2) >= 2:
                fired.append("rule_2: two of three consecutive beyond 2 sigma")
                break
        else:
            continue
        break

    # Rule 3 — four of five consecutive beyond 1 sigma, same side.
    for i in range(len(z) - 4):
        window = z[i : i + 5]
        for side in (1, -1):
            if sum(1 for x in window if x * side > 1) >= 4:
                fired.append("rule_3: four of five consecutive beyond 1 sigma")
                break
        else:
            continue
        break

    # Rule 4 — eight consecutive on one side of the mean. Drift, not a spike.
    for i in range(len(z) - 7):
        window = z[i : i + 8]
        if all(x > 0 for x in window) or all(x < 0 for x in window):
            fired.append("rule_4: eight consecutive on one side of the mean")
            break

    rules = gate.load_yaml("ops/response-tiers.yaml")["western_electric"]
    tiers = [rules[f.split(":")[0]]["tier"] for f in fired]
    tier = max(tiers, key=TIER_ORDER.index) if tiers else "none"

    return {
        "tier": tier,
        "rules_fired": fired,
        "mean": round(mean, 6),
        "stdev": round(sd, 6),
        "latest": recent[-1] if recent else None,
        "latest_sigma": round(z[-1], 3) if z else None,
        # A lead for triage, not a conclusion. Named so a person starts somewhere
        # instead of starting with a number.
        "suspect_deploy": correlate(z, deploys or []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--metrics",
        default="ops/fixtures/post_deploy_error_rate.json",
        help="JSON with {history: [...], recent: [...]}. In production this is an "
        "observability query; the fixture keeps the demo reproducible.",
    )
    args = parser.parse_args()

    config = gate.load_yaml("ops/response-tiers.yaml")
    data = json.loads((gate.ROOT / args.metrics).read_text())
    result = evaluate(data["history"], data["recent"], data.get("deploys", []))

    action = config["tiers"].get(result["tier"], {}).get("action", "none")
    result["action"] = action
    result["metric"] = config["metric"]
    result["autonomy_tier"] = config["actions"].get(action, {}).get("autonomy_tier", "A0")

    print(json.dumps(result, indent=2))

    # Machine-readable for the workflow to branch on.
    if out := __import__("os").environ.get("GITHUB_OUTPUT"):
        with open(out, "a") as fh:
            fh.write(f"tier={result['tier']}\naction={action}\n")
            # The metric name, so the workflow can ask whether this excursion is already
            # tracked before raising a second finding for it. Computed here already; it
            # simply was not emitted, and the cost of that was three identical findings.
            fh.write(f"metric={result['metric']}\n")
            fh.write(f"sigma={result['latest_sigma']}\n")
            fh.write(f"rules={'; '.join(result['rules_fired'])}\n")
            suspect = result.get("suspect_deploy") or {}
            fh.write(f"suspect_deploy={suspect.get('ref', '')}\n")

    # A breach is not a gate failure — it is a finding. The gate always passes;
    # the evidence records what was detected and at what tier.
    return gate.report("OPS-01", "anomaly_detection", True, [], **result)


if __name__ == "__main__":
    raise SystemExit(main())

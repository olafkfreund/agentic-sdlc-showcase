"""Stage 6.2 requires the detection script be version-controlled and unit-tested.

These are the tests. A detector nobody tested is a control nobody can evidence.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import detect_anomaly as d  # noqa: E402

# Baseline: mean 10.0, sd ~0.8305 (sqrt(20/29)). Bands: 1s 10.83 | 2s 11.66 | 3s 12.49.
STABLE = [9.0, 10.0, 11.0] * 10


def test_baseline_needs_two_points():
    with pytest.raises(ValueError):
        d.baseline([1.0])


def test_sigmas_is_zero_when_the_baseline_is_flat():
    assert d.sigmas(5.0, 5.0, 0.0) == 0.0


def test_quiet_series_fires_nothing():
    assert d.evaluate(STABLE, [10.0, 9.5, 10.5, 10.0])["tier"] == "none"


def test_single_spike_is_3sigma():
    result = d.evaluate(STABLE, [10.0, 10.0, 40.0])
    assert result["tier"] == "3sigma"
    assert any("rule_1" in r for r in result["rules_fired"])


def test_two_of_three_beyond_2sigma_is_2sigma():
    # Between the 2s and 3s bands, so rule_2 fires and rule_1 does not.
    result = d.evaluate(STABLE, [12.0, 10.0, 12.1])
    assert result["tier"] == "2sigma"
    assert any("rule_2" in r for r in result["rules_fired"])


def test_four_of_five_beyond_1sigma_is_2sigma():
    # All five between the 1s and 2s bands, so only rule_3 can fire.
    result = d.evaluate(STABLE, [11.0, 11.1, 10.0, 11.2, 11.3])
    assert any("rule_3" in r for r in result["rules_fired"])
    assert result["tier"] == "2sigma"


def test_drift_is_caught_without_any_spike():
    """Eight consecutive on one side. No single point is even 2 sigma out.

    This is the case a simple threshold never catches and which is usually the
    more expensive problem.
    """
    result = d.evaluate(STABLE, [10.4] * 8)
    assert result["tier"] == "1sigma"
    assert any("rule_4" in r for r in result["rules_fired"])
    assert all(abs(d.sigmas(v, 10.0, result["stdev"])) < 2 for v in [10.4] * 8)


def test_a_downward_run_also_fires():
    """Errors dropping to zero is as suspicious as errors spiking."""
    assert d.evaluate(STABLE, [9.6] * 8)["tier"] == "1sigma"


def test_the_highest_tier_wins_when_several_rules_fire():
    result = d.evaluate(STABLE, [12.0, 12.1, 12.2, 12.3, 40.0])
    assert len(result["rules_fired"]) > 1
    assert result["tier"] == "3sigma"


def test_the_shipped_fixture_reaches_3sigma():
    """The demo depends on this. If the fixture drifts, the walkthrough breaks."""
    import json

    data = json.loads((d.gate.ROOT / "ops/fixtures/post_deploy_error_rate.json").read_text())
    result = d.evaluate(data["history"], data["recent"])
    assert result["tier"] == "3sigma"
    assert result["latest_sigma"] > 3


# --- Deploy correlation (CHG-2026-014902) ---------------------------------------
#
# Which deploy was live when the breach began. Arithmetic over two ordered arrays,
# so it stays as deterministic and testable as the detection it rides along with.

BREACH = [10.0, 10.0, 40.0, 40.0]  # breaches from index 2


def z_of(recent):
    mean, sd = d.baseline(STABLE)
    return [d.sigmas(v, mean, sd) for v in recent]


def test_correlate_names_the_deploy_before_the_breach():
    deploys = [{"index": 1, "ref": "v1.4.0"}]
    assert d.correlate(z_of(BREACH), deploys)["ref"] == "v1.4.0"


def test_a_deploy_after_the_breach_is_not_blamed():
    """The obvious off-by-one, and it would send triage to the wrong team."""
    deploys = [{"index": 3, "ref": "v1.5.0"}]
    assert d.correlate(z_of(BREACH), deploys) is None


def test_the_most_recent_prior_deploy_wins():
    deploys = [
        {"index": 0, "ref": "v1.3.0"},
        {"index": 2, "ref": "v1.4.0"},
        {"index": 3, "ref": "v1.5.0"},
    ]
    # index 2 is the first breaching observation, so a marker *at* it counts.
    assert d.correlate(z_of(BREACH), deploys)["ref"] == "v1.4.0"


def test_no_deploy_markers_yields_none():
    """Returns None rather than raising. A detector that can fail gets switched off."""
    assert d.correlate(z_of(BREACH), []) is None


def test_no_breach_yields_none():
    quiet = z_of([10.0, 9.5, 10.5])
    assert d.correlate(quiet, [{"index": 0, "ref": "v1.3.0"}]) is None


def test_the_shipped_fixture_names_a_suspect_deploy():
    """The walkthrough depends on this: triage should start with a suspect."""
    import json

    data = json.loads((d.gate.ROOT / "ops/fixtures/post_deploy_error_rate.json").read_text())
    result = d.evaluate(data["history"], data["recent"], data.get("deploys", []))
    assert result["suspect_deploy"] is not None
    assert result["suspect_deploy"]["ref"]


def test_evaluate_without_deploys_still_works():
    """Additive: the existing callers pass no markers and must be unaffected."""
    assert d.evaluate(STABLE, [10.0, 10.0, 40.0])["suspect_deploy"] is None


def test_github_output_carries_the_metric_name(tmp_path, monkeypatch):
    """The workflow branches on these keys, so they are an interface, not a debug print.

    `metric` is the one the dedupe lookup needs: without it the workflow cannot ask whether
    this excursion is already tracked, and raises a fresh finding every night. Three
    identical 6.926 sigma findings were filed before this key existed.
    """
    import detect_anomaly

    out = tmp_path / "gh_output"
    out.write_text("")
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))
    monkeypatch.setattr(
        "sys.argv",
        ["detect_anomaly.py", "--metrics", "ops/fixtures/post_deploy_error_rate.json"],
    )
    detect_anomaly.main()

    emitted = dict(line.split("=", 1) for line in out.read_text().splitlines() if "=" in line)
    assert emitted["metric"] == "post_deploy_error_rate"
    # The rest of the interface, so a rename shows up here rather than in a silent workflow.
    assert {"tier", "action", "sigma", "rules", "suspect_deploy"} <= emitted.keys()

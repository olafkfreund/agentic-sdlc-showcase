"""The §6.2 supervisory query. It answers the question that arrives in a review,
so it is worth a test that it does not fall over on its own evidence directory.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import query_evidence as qe  # noqa: E402


def test_skips_aggregates_that_carry_no_control_id(tmp_path, monkeypatch):
    """bundle.json is an aggregate of gate results, not one of them.

    Reading it as a result raised KeyError('control_id') and took the whole query
    down — the query being the thing that answers a supervisor in minutes rather
    than a week.
    """
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    (evidence / "pii.json").write_text(json.dumps({"control_id": "DP-11", "result": "pass"}))
    (evidence / "bundle.json").write_text(json.dumps({"all_passed": True, "results": []}))
    (evidence / "broken.json").write_text("{not json")
    monkeypatch.setattr(qe.gate, "ROOT", tmp_path)

    records = qe.evidence_records()
    assert [r["control_id"] for r in records] == ["DP-11"]


def test_quarter_of():
    from datetime import datetime

    assert qe.quarter_of(datetime(2026, 4, 1)) == "2026Q2"
    assert qe.quarter_of(datetime(2026, 12, 31)) == "2026Q4"
    assert qe.quarter_of(datetime(2026, 3, 31)) == "2026Q1"

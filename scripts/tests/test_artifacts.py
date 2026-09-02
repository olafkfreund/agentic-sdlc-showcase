"""The §6.2 header, and the terminal states a chain may stop in.

Three chains stopped before a plan and said nothing about it, so a deliberate halt and an
abandoned change were the same shape on disk. `CHG-04` missed it because it enforced the
chain backwards only — a plan implies a spec implies an intent — and never forwards.
"""

from __future__ import annotations

import sys

sys.path.insert(0, __file__.rsplit("/", 2)[0])

import artifacts  # noqa: E402

BASE = {
    "change_id": "CHG-2026-000001",
    "risk_class": "R2",
    "autonomy_tier": "A2",
    "controls": ["CHG-04"],
    "data_classification": "internal",
    "originator": "someone@example.com",
    "agent_identity": "svc-agent-platform",
    "model_route": "gateway/tier-balanced",
}


def test_a_header_without_a_status_is_valid():
    """Absent means active. Every artifact written before the field existed stays valid,
    which is why nothing had to be backfilled."""
    assert artifacts.validate(dict(BASE)) == []


def test_both_terminal_states_are_accepted():
    for status in ("blocked", "dismissed"):
        errors = artifacts.validate({**BASE, "status": status, "status_reason": "because"})
        assert errors == [], (status, errors)


def test_an_unknown_status_is_rejected():
    errors = artifacts.validate({**BASE, "status": "wontfix", "status_reason": "because"})
    assert any("status must be one of" in e for e in errors), errors


def test_a_status_without_a_reason_is_rejected():
    """`blocked` with no reason is the original gap wearing a label: the chain still does
    not say why it stopped, it just admits that it did."""
    errors = artifacts.validate({**BASE, "status": "blocked"})
    assert any("requires a status_reason" in e for e in errors), errors
    errors = artifacts.validate({**BASE, "status": "blocked", "status_reason": "   "})
    assert any("requires a status_reason" in e for e in errors), errors


def test_a_reason_without_a_status_is_rejected():
    """A note nothing can query is not evidence."""
    errors = artifacts.validate({**BASE, "status_reason": "we gave up"})
    assert any("without a status" in e for e in errors), errors


def test_every_stopped_chain_in_this_repository_says_why():
    """Not a unit test — an assertion about this repository, and the one that matters.

    A chain reaching a plan needs no status. Any other chain must declare one, or it is
    indistinguishable from an abandoned change.
    """
    seen = {a.change_id for a in artifacts.all_artifacts() if a.change_id}
    for change_id in sorted(seen):
        chain = artifacts.chain(change_id)
        if "plan" in chain:
            continue
        last = chain.get("spec") or chain.get("intent")
        assert last is not None, change_id
        status = last.header.get("status")
        assert status in artifacts.STATUSES, (
            f"{change_id} stops at {last.stage} with no plan and no status"
        )
        assert str(last.header.get("status_reason", "")).strip(), change_id

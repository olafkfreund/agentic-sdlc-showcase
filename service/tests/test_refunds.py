"""Refunds against a settled payment — CHG-2026-014882.

The tests the plan named, in the order it named them.
"""

import json

import pytest
from fastapi.testclient import TestClient

from service.app import audit, main
from service.app.main import app

client = TestClient(app)
AUTH = {"X-Gateway-Token": "test-gateway-token"}
OPERATOR = "ops.hendricks@example.com"

PAYMENT = {
    "amount": "10.50",
    "currency": "GBP",
    "payer_name": "Ada Lovelace",
    "payer_email": "ada.lovelace@example.com",
    "payer_account": "GB29NWBK60161331926819",
    "reference": "INV-001",
}


@pytest.fixture
def settled_payment():
    payment_id = client.post("/payments", json=PAYMENT, headers=AUTH).json()["payment_id"]
    main.settle(payment_id)
    yield payment_id
    main._REFUNDS.pop(payment_id, None)


@pytest.fixture
def accepted_payment():
    return client.post("/payments", json=PAYMENT, headers=AUTH).json()["payment_id"]


def refund(payment_id, **overrides):
    body = {"operator_id": OPERATOR, "reason": "customer dispute", **overrides}
    return client.post(f"/payments/{payment_id}/refunds", json=body, headers=AUTH)


def test_full_refund_succeeds(settled_payment):
    response = refund(settled_payment)
    assert response.status_code == 201
    body = response.json()
    assert body["payment_id"] == settled_payment
    assert body["amount"] == "10.50"
    assert body["status"] == "refunded"


def test_second_refund_is_conflict(settled_payment):
    """R2 — the failure mode that paid two refunds for one dispute last month."""
    assert refund(settled_payment).status_code == 201
    second = refund(settled_payment)
    assert second.status_code == 409
    assert "already been refunded" in second.json()["detail"]


def test_unsettled_payment_is_422(accepted_payment):
    response = refund(accepted_payment)
    assert response.status_code == 422
    assert "settled" in response.json()["detail"]


def test_unknown_payment_is_404():
    assert refund("no-such-payment").status_code == 404


def test_operator_id_never_logged(settled_payment, caplog):
    """DP-11. This is the test that would have caught INC-2026-0431."""
    with caplog.at_level("INFO", logger="payments"):
        assert refund(settled_payment).status_code == 201
    assert OPERATOR not in caplog.text


def test_operator_id_is_not_in_the_response(settled_payment):
    body = refund(settled_payment).json()
    assert "operator_id" not in body
    assert OPERATOR not in json.dumps(body)


def test_error_messages_do_not_echo_the_request(accepted_payment):
    assert OPERATOR not in refund(accepted_payment).text


def test_the_payment_row_is_not_mutated(settled_payment):
    """Reconciliation reads payments as an append-only log; refunded is derived."""
    refund(settled_payment)
    assert main._STORE[settled_payment]["status"] == "settled"
    assert client.get(f"/payments/{settled_payment}", headers=AUTH).json()["status"] == "refunded"


def test_refund_requires_the_gateway_token(settled_payment):
    response = client.post(f"/payments/{settled_payment}/refunds", json={"operator_id": OPERATOR})
    assert response.status_code == 401


def test_refund_emits_an_audit_event(settled_payment):
    before = len(audit.EVENTS)
    refund_id = refund(settled_payment).json()["refund_id"]
    assert len(audit.EVENTS) == before + 1
    event = audit.EVENTS[-1]
    assert event["action"] == "payment.refund"
    assert event["entity"] == refund_id
    assert event["actor"] == "test-gateway-token"
    assert event["minor_units"] == 1050
    assert OPERATOR not in json.dumps(event)

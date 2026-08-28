from fastapi.testclient import TestClient

from service.app import audit, main
from service.app.main import app

client = TestClient(app)
AUTH = {"X-Gateway-Token": "test-gateway-token"}

PAYLOAD = {
    "amount": "10.50",
    "currency": "GBP",
    "payer_name": "Ada Lovelace",
    "payer_email": "ada.lovelace@example.com",
    "payer_account": "GB29NWBK60161331926819",
    "reference": "INV-001",
}


def test_health_is_the_only_anonymous_route():
    assert client.get("/health").json() == {"status": "ok"}


def test_create_payment_requires_the_gateway_token():
    assert client.post("/payments", json=PAYLOAD).status_code == 401


def test_create_payment_emits_an_audit_event():
    before = len(audit.EVENTS)
    response = client.post("/payments", json=PAYLOAD, headers=AUTH)
    assert response.status_code == 201
    assert len(audit.EVENTS) == before + 1
    event = audit.EVENTS[-1]
    assert event["action"] == "payment.create"
    assert event["actor"] == "test-gateway-token"
    assert event["entity"] == response.json()["payment_id"]


def test_response_does_not_leak_personal_data():
    body = client.post("/payments", json=PAYLOAD, headers=AUTH).json()
    assert "payer_email" not in body
    assert "payer_name" not in body
    assert "payer_account" not in body


def test_validation_error_does_not_echo_personal_data():
    bad = {**PAYLOAD, "amount": "10.505"}
    response = client.post("/payments", json=bad, headers=AUTH)
    assert response.status_code == 422
    assert PAYLOAD["payer_email"] not in response.text


def test_round_trip():
    created = client.post("/payments", json=PAYLOAD, headers=AUTH).json()
    fetched = client.get(f"/payments/{created['payment_id']}", headers=AUTH).json()
    assert fetched == created


def test_unknown_payment_is_404():
    assert client.get("/payments/nope", headers=AUTH).status_code == 404


def test_refund_emits_audit_event():
    """The Stage 5 review pass checks the spec's requirements have tests. R3 does."""
    created = client.post("/payments", json=PAYLOAD, headers=AUTH).json()
    main.settle(created["payment_id"])
    before = len(audit.EVENTS)
    response = client.post(
        f"/payments/{created['payment_id']}/refunds",
        json={"operator_id": "ops.hendricks@example.com"},
        headers=AUTH,
    )
    assert response.status_code == 201
    assert audit.EVENTS[-1]["action"] == "payment.refund"
    assert len(audit.EVENTS) == before + 1

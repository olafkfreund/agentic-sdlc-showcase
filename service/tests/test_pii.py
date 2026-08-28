"""Fields classified `personal` must never reach a log line or an audit event."""

import json

from service.app import audit
from service.app.models import PERSONAL_FIELDS

SECRET = "ada.lovelace@example.com"


def test_redact_drops_personal_fields():
    out = audit.redact({"amount": "1.00", "payer_email": SECRET})
    assert out == {"amount": "1.00"}


def test_safe_log_never_writes_personal_data(caplog):
    with caplog.at_level("INFO", logger="payments"):
        audit.safe_log("created", payment_id="p1", payer_email=SECRET, payer_name="Ada")
    written = caplog.text
    assert SECRET not in written
    assert "Ada" not in written
    assert json.loads(caplog.records[-1].getMessage())["payment_id"] == "p1"


def test_audit_event_never_carries_personal_data():
    event = audit.emit(actor="svc", action="payment.create", entity="p1", payer_email=SECRET)
    assert SECRET not in json.dumps(event)
    assert not (PERSONAL_FIELDS & event.keys())

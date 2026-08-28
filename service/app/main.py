"""HTTP routes. No domain logic here — see AGENTS.md Architecture."""

import uuid

from fastapi import FastAPI, Header, HTTPException

from . import audit, money
from .models import PaymentRequest, PaymentResponse, RefundRequest, RefundResponse

app = FastAPI(title="payments-service", version="1.0.0")

# ponytail: in-memory store. A demo does not need Postgres to prove a gate fires.
_STORE: dict[str, dict] = {}

# Refunds live beside payments rather than mutating them: reconciliation reads
# payments as an append-only log, and a mutable row breaks that assumption silently
# (spec CHG-2026-014882, rejected alternative 1).
#
# Keyed on payment_id, so "one refund per payment" is a uniqueness constraint rather
# than a check-then-act. Full refunds only for now; when partial refunds arrive the
# key becomes (payment_id, idempotency_key) — noted in the spec so the migration is
# expected rather than discovered.
_REFUNDS: dict[str, dict] = {}


def settle(payment_id: str) -> None:
    """Mark a payment settled.

    Settlement is an external event — the provider tells us, and wiring that up is a
    separate change with its own record. This stands in for the provider webhook so
    the settled-only rule has something to test against.
    """
    if payment_id in _STORE:
        _STORE[payment_id]["status"] = "settled"


@app.get("/health")
def health() -> dict:
    """The only anonymous route (AGENTS.md / secure-api-review rule 1)."""
    return {"status": "ok"}


def _actor(token: str | None) -> str:
    if not token:
        raise HTTPException(status_code=401, detail="gateway token required")
    return token


@app.post("/payments", response_model=PaymentResponse, status_code=201)
def create_payment(
    request: PaymentRequest,
    x_gateway_token: str | None = Header(default=None),
) -> PaymentResponse:
    actor = _actor(x_gateway_token)
    try:
        amount, currency = money.parse(request.amount, request.currency)
    except money.MoneyError as exc:
        # The message must not echo the payer's details back — they are personal data.
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    payment_id = str(uuid.uuid4())
    record = {
        "payment_id": payment_id,
        "amount": str(amount),
        "currency": currency,
        "status": "accepted",
        "reference": request.reference,
        "payer_name": request.payer_name,
        "payer_email": request.payer_email,
        "payer_account": request.payer_account,
    }
    _STORE[payment_id] = record

    audit.emit(
        actor=actor,
        action="payment.create",
        entity=payment_id,
        amount=str(amount),
        currency=currency,
        minor_units=money.format_minor(amount),
    )
    return PaymentResponse(**{k: record[k] for k in PaymentResponse.model_fields})


@app.post("/payments/{payment_id}/refunds", response_model=RefundResponse, status_code=201)
def create_refund(
    payment_id: str,
    request: RefundRequest,
    x_gateway_token: str | None = Header(default=None),
) -> RefundResponse:
    actor = _actor(x_gateway_token)

    record = _STORE.get(payment_id)
    if record is None:
        raise HTTPException(status_code=404, detail="payment not found")
    if record["status"] != "settled":
        # The reason, never the payload. An error that echoes the request body is a
        # data-protection incident with a stack trace attached.
        raise HTTPException(
            status_code=422,
            detail=f"only a settled payment may be refunded, not {record['status']!r}",
        )

    refund = {
        "refund_id": str(uuid.uuid4()),
        "payment_id": payment_id,
        "amount": record["amount"],
        "currency": record["currency"],
        "status": "refunded",
        "operator_id": request.operator_id,
        "reason": request.reason,
    }
    # setdefault is the constraint: two concurrent requests cannot both win, which an
    # `if payment_id not in _REFUNDS` check could not promise.
    existing = _REFUNDS.setdefault(payment_id, refund)
    if existing is not refund:
        raise HTTPException(status_code=409, detail="payment has already been refunded")

    audit.emit(
        actor=actor,
        action="payment.refund",
        entity=refund["refund_id"],
        payment_id=payment_id,
        amount=refund["amount"],
        currency=refund["currency"],
        minor_units=money.format_minor(money.parse(refund["amount"], refund["currency"])[0]),
    )
    return RefundResponse(**{k: refund[k] for k in RefundResponse.model_fields})


@app.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: str,
    x_gateway_token: str | None = Header(default=None),
) -> PaymentResponse:
    _actor(x_gateway_token)
    record = _STORE.get(payment_id)
    if record is None:
        raise HTTPException(status_code=404, detail="payment not found")
    fields = {k: record[k] for k in PaymentResponse.model_fields}
    if payment_id in _REFUNDS:
        fields["status"] = "refunded"  # derived, so the payment row stays immutable
    return PaymentResponse(**fields)

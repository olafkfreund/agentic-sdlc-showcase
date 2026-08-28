"""Request/response models and the data classification map."""

from pydantic import BaseModel, Field

# Fields classified `personal` must never reach a log line or an error message.
# scripts/check_pii.py and service/tests/test_pii.py both enforce this.
CLASSIFICATION: dict[str, str] = {
    "payment_id": "internal",
    "amount": "internal",
    "currency": "internal",
    "status": "internal",
    "payer_name": "personal",
    "payer_email": "personal",
    "payer_account": "personal",
    "reference": "internal",
    "refund_id": "internal",
    "operator_id": "personal",
}

PERSONAL_FIELDS = frozenset(k for k, v in CLASSIFICATION.items() if v == "personal")


class PaymentRequest(BaseModel):
    amount: str = Field(description="Decimal amount as a string, e.g. '10.50'")
    currency: str
    payer_name: str
    payer_email: str
    payer_account: str
    reference: str = ""


class PaymentResponse(BaseModel):
    payment_id: str
    amount: str
    currency: str
    status: str
    reference: str


class RefundRequest(BaseModel):
    operator_id: str = Field(description="The operator issuing the refund. Personal data.")
    reason: str = ""


class RefundResponse(BaseModel):
    refund_id: str
    payment_id: str
    amount: str
    currency: str
    status: str

"""Monetary primitives. Decimal only — see AGENTS.md Conventions."""

from decimal import ROUND_HALF_EVEN, Decimal

# ponytail: two-place minor units cover every currency this demo accepts.
# Add a per-currency exponent table when JPY/KWD show up.
_CENTS = Decimal("0.01")

SUPPORTED = frozenset({"GBP", "EUR", "USD"})


class MoneyError(ValueError):
    """Raised when an amount or currency is not representable."""


def parse(amount: str, currency: str) -> tuple[Decimal, str]:
    """Parse a monetary amount from its string form.

    Strings, never floats: `float("0.1") + float("0.2") != 0.3`, and a payments
    ledger that is out by a hundredth is a reconciliation incident.
    """
    if not isinstance(amount, str):
        raise MoneyError("amount must be a string, not a float or int")
    currency = currency.upper()
    if currency not in SUPPORTED:
        raise MoneyError(f"unsupported currency: {currency}")
    try:
        value = Decimal(amount)
    except Exception as exc:  # noqa: BLE001 - Decimal raises several types
        raise MoneyError(f"not a decimal amount: {amount!r}") from exc
    if value <= 0:
        raise MoneyError("amount must be positive")
    if value != value.quantize(_CENTS, rounding=ROUND_HALF_EVEN):
        raise MoneyError("amount has more precision than the currency's minor unit")
    return value, currency


def add(a: Decimal, b: Decimal) -> Decimal:
    """Sum two amounts, quantised to the minor unit with banker's rounding."""
    return (a + b).quantize(_CENTS, rounding=ROUND_HALF_EVEN)


def format_minor(value: Decimal) -> int:
    """Render an amount as an integer number of minor units, for the ledger."""
    return int(value.quantize(_CENTS, rounding=ROUND_HALF_EVEN) * 100)

from decimal import Decimal

import pytest

from service.app import money


def test_parses_a_decimal_string():
    assert money.parse("10.50", "GBP") == (Decimal("10.50"), "GBP")


def test_rejects_a_float():
    with pytest.raises(money.MoneyError, match="must be a string"):
        money.parse(10.50, "GBP")  # type: ignore[arg-type]


def test_rejects_sub_minor_unit_precision():
    with pytest.raises(money.MoneyError, match="precision"):
        money.parse("10.505", "GBP")


def test_rejects_unsupported_currency():
    with pytest.raises(money.MoneyError, match="unsupported currency"):
        money.parse("1.00", "XBT")


@pytest.mark.parametrize("amount", ["0.00", "-1.00"])
def test_rejects_non_positive(amount):
    with pytest.raises(money.MoneyError, match="positive"):
        money.parse(amount, "GBP")


def test_addition_is_exact_where_float_is_not():
    a, _ = money.parse("0.10", "GBP")
    b, _ = money.parse("0.20", "GBP")
    assert money.add(a, b) == Decimal("0.30")
    assert 0.1 + 0.2 != 0.3  # the reason this module exists


def test_minor_units():
    assert money.format_minor(Decimal("10.50")) == 1050

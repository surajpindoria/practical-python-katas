from decimal import Decimal

import pytest

from money import CurrencyMismatchError, Money


# -------------------------------------------------------------- construction

def test_construct_from_str_int_decimal():
    assert Money("12.5").amount == Decimal("12.50")
    assert Money(3).amount == Decimal("3.00")
    assert Money(Decimal("7.1")).amount == Decimal("7.10")


def test_amount_is_quantized_half_up():
    assert Money("1.005").amount == Decimal("1.01")
    assert Money("1.004").amount == Decimal("1.00")
    assert str(Money("2").amount) == "2.00"


def test_default_currency_and_normalization():
    assert Money("1").currency == "USD"
    assert Money("1", "eur").currency == "EUR"


def test_float_rejected():
    with pytest.raises(TypeError):
        Money(1.5)


def test_bad_amount_string():
    with pytest.raises(ValueError):
        Money("abc")


@pytest.mark.parametrize("cur", ["US", "USDD", "12A", "", "U$D"])
def test_bad_currency(cur):
    with pytest.raises(ValueError):
        Money("1", cur)


def test_immutable():
    m = Money("1")
    with pytest.raises(AttributeError):
        m.amount = Decimal("5")
    with pytest.raises(AttributeError):
        m.currency = "EUR"


# ---------------------------------------------------------------- arithmetic

def test_add_and_sub():
    assert Money("1.10") + Money("2.20") == Money("3.30")
    assert Money("5") - Money("7.5") == Money("-2.50")


def test_add_mismatch():
    with pytest.raises(CurrencyMismatchError):
        Money("1", "USD") + Money("1", "EUR")
    with pytest.raises(CurrencyMismatchError):
        Money("1", "USD") - Money("1", "EUR")


def test_currency_mismatch_is_value_error():
    assert issubclass(CurrencyMismatchError, ValueError)


def test_add_non_money_type_error():
    with pytest.raises(TypeError):
        Money("1") + 5
    with pytest.raises(TypeError):
        Money("1") + "1"


def test_sum_builtin():
    assert sum([Money("1.00"), Money("2.00"), Money("0.50")]) == Money("3.50")


def test_multiply():
    assert Money("10.00") * 3 == Money("30.00")
    assert 3 * Money("10.00") == Money("30.00")
    assert Money("10.00") * Decimal("0.333") == Money("3.33")
    assert Money("10.00") * Decimal("0.3335") == Money("3.34")


def test_multiply_bad_types():
    with pytest.raises(TypeError):
        Money("1") * 1.5
    with pytest.raises(TypeError):
        Money("1") * Money("1")


def test_neg_and_bool():
    assert -Money("3") == Money("-3")
    assert not Money("0")
    assert Money("0.01")


def test_operations_return_new_objects():
    a = Money("1")
    b = a + Money("1")
    assert a == Money("1")
    assert b is not a


# ------------------------------------------------------ equality & ordering

def test_equality():
    assert Money("1", "USD") == Money("1.00", "usd")
    assert Money("1", "USD") != Money("1", "EUR")
    assert Money("1") != "1.00 USD"
    assert Money("1") != 1


def test_hashable():
    assert hash(Money("1.0")) == hash(Money("1.00"))
    s = {Money("1"), Money("1.00"), Money("1", "EUR")}
    assert len(s) == 2


def test_ordering():
    assert Money("1") < Money("2")
    assert Money("2") >= Money("2")
    assert max([Money("3"), Money("10"), Money("7")]) == Money("10")


def test_ordering_mismatch():
    with pytest.raises(CurrencyMismatchError):
        Money("1", "USD") < Money("2", "EUR")


# -------------------------------------------------------------- formatting

def test_repr_and_str():
    assert repr(Money("12.5")) == "Money('12.50', 'USD')"
    assert str(Money("12.5", "gbp")) == "12.50 GBP"
    assert str(Money("-3")) == "-3.00 USD"


# ---------------------------------------------------------------- allocate

def test_allocate_even_with_remainder():
    parts = Money("10.00").allocate([1, 1, 1])
    assert parts == [Money("3.34"), Money("3.33"), Money("3.33")]


def test_allocate_weighted():
    assert Money("0.05").allocate([70, 30]) == [Money("0.04"), Money("0.01")]
    assert Money("100").allocate([1, 3]) == [Money("25"), Money("75")]


def test_allocate_preserves_total_and_currency():
    m = Money("1234.57", "EUR")
    parts = m.allocate([3, 7, 11, 13])
    assert sum(parts) == m
    assert all(p.currency == "EUR" for p in parts)


def test_allocate_zero_ratio():
    assert Money("1.00").allocate([0, 1]) == [Money("0"), Money("1")]


@pytest.mark.parametrize("ratios", [[], [0, 0], [1, -1]])
def test_allocate_bad_ratios(ratios):
    with pytest.raises(ValueError):
        Money("1").allocate(ratios)

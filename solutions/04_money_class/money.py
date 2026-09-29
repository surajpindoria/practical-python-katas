"""04 - Money Value Object: reference solution."""
import functools
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Self

CENT = Decimal("0.01")


class CurrencyMismatchError(ValueError):
    """Raised when combining or comparing Money of different currencies."""


def _to_decimal(amount: object) -> Decimal:
    # bool is a subclass of int, so it has to be excluded explicitly.
    if isinstance(amount, (bool, float)) or not isinstance(amount, (str, int, Decimal)):
        raise TypeError("amount must be str, int or Decimal")
    try:
        value = Decimal(amount)
    except InvalidOperation:
        raise ValueError(f"invalid amount {amount!r}") from None
    if not value.is_finite():
        raise ValueError("amount must be finite")
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


@functools.total_ordering  # derives <=, >, >= from __eq__ and __lt__
@dataclass(frozen=True, eq=False)  # frozen: assignment raises FrozenInstanceError (an AttributeError)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        cur = self.currency
        if not (isinstance(cur, str) and len(cur) == 3 and cur.isascii() and cur.isalpha()):
            raise ValueError(f"invalid currency {cur!r}")
        # Frozen dataclasses must bypass their own __setattr__ to normalize fields.
        object.__setattr__(self, "amount", _to_decimal(self.amount))
        object.__setattr__(self, "currency", cur.upper())

    def _same_currency(self, other: object) -> bool:
        """False for non-Money (so callers return NotImplemented). Raises on a currency mismatch."""
        if not isinstance(other, Money):
            return False
        if other.currency != self.currency:
            raise CurrencyMismatchError(f"{self.currency} vs {other.currency}")
        return True

    # Returning NotImplemented (instead of raising) lets Python try the other
    # operand's reflected method, and raise TypeError if that fails too.
    def __add__(self, other: object) -> Self:
        if not self._same_currency(other):
            return NotImplemented
        return Money(self.amount + other.amount, self.currency)

    def __radd__(self, other: object) -> Self:
        # sum() starts from 0, so 0 + Money must work.
        if other == 0 and not isinstance(other, bool):
            return self
        return NotImplemented

    def __sub__(self, other: object) -> Self:
        if not self._same_currency(other):
            return NotImplemented
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, n: object) -> Self:
        if isinstance(n, bool) or not isinstance(n, (int, Decimal)):
            return NotImplemented
        return Money(self.amount * n, self.currency)

    __rmul__ = __mul__

    def __neg__(self) -> Self:
        return Money(-self.amount, self.currency)

    def __bool__(self) -> bool:
        return bool(self.amount)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return (self.amount, self.currency) == (other.amount, other.currency)

    def __hash__(self) -> int:  # defining __eq__ removes the default __hash__, so define it again
        return hash((self.amount, self.currency))

    def __lt__(self, other: object) -> bool:
        if not self._same_currency(other):
            return NotImplemented
        return self.amount < other.amount

    def __repr__(self) -> str:
        return f"Money('{self.amount}', '{self.currency}')"

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"

    def allocate(self, ratios: list[int]) -> list[Self]:
        if not ratios or any(r < 0 for r in ratios) or sum(ratios) == 0:
            raise ValueError("ratios must be non-empty, non-negative and not all zero")
        # Work in integer cents so no rounding error is possible.
        cents = int(self.amount / CENT)
        total = sum(ratios)
        shares = [cents * r // total for r in ratios]
        for i in range(cents - sum(shares)):  # hand out the leftover cents one by one
            shares[i] += 1
        return [Money(Decimal(s) * CENT, self.currency) for s in shares]

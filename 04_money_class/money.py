"""04 - Money Value Object. See README.md for the full specification."""
from decimal import Decimal
from typing import Self


class CurrencyMismatchError(ValueError):
    """Raised when combining or comparing Money of different currencies."""


class Money:
    def __init__(self, amount: str | int | Decimal, currency: str = "USD") -> None:
        raise NotImplementedError

    # Implement the dunder methods and properties described in the README.

    def allocate(self, ratios: list[int]) -> list[Self]:
        raise NotImplementedError

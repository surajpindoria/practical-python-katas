"""02 - Expense Report. See README.md for the full specification."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

type PathLike = str | Path


@dataclass(frozen=True)
class Expense:
    date: date
    employee: str
    category: str
    amount: Decimal


def load_expenses(path: PathLike) -> tuple[list[Expense], list[int]]:
    raise NotImplementedError


def totals_by_category(expenses: list[Expense]) -> dict[str, Decimal]:
    raise NotImplementedError


def monthly_report(expenses: list[Expense]) -> dict[str, dict[str, Decimal]]:
    raise NotImplementedError


def write_summary(expenses: list[Expense], path: PathLike) -> None:
    raise NotImplementedError

"""02 - Expense Report: reference solution."""
import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

type PathLike = str | Path


@dataclass(frozen=True)
class Expense:
    date: date
    employee: str
    category: str
    amount: Decimal


def _parse_row(row: dict[str, str]) -> Expense:
    """Build an Expense from a CSV row, raising ValueError/InvalidOperation if invalid."""
    expense_date = date.fromisoformat(row["date"].strip())
    employee = row["employee"].strip()
    if not employee:
        raise ValueError("empty employee")
    amount = Decimal(row["amount"].strip())  # never float(): money needs exact decimals
    if not amount.is_finite() or amount < 0:
        raise ValueError("invalid amount")
    return Expense(expense_date, employee, row["category"].strip().lower(), amount)


def load_expenses(path: PathLike) -> tuple[list[Expense], list[int]]:
    expenses: list[Expense] = []
    bad: list[int] = []
    with open(path, newline="") as f:  # newline="" is what the csv module expects
        reader = csv.DictReader(f)
        for row in reader:
            try:
                expenses.append(_parse_row(row))
            except (ValueError, InvalidOperation, AttributeError):
                # reader.line_num is the physical line number, header included
                bad.append(reader.line_num)
    return expenses, bad


def totals_by_category(expenses: list[Expense]) -> dict[str, Decimal]:
    totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    for e in expenses:
        totals[e.category] += e.amount
    return dict(totals)


def monthly_report(expenses: list[Expense]) -> dict[str, dict[str, Decimal]]:
    report: defaultdict[str, defaultdict[str, Decimal]] = defaultdict(lambda: defaultdict(Decimal))
    for e in expenses:
        report[f"{e.date:%Y-%m}"][e.category] += e.amount
    # "YYYY-MM" strings sort chronologically.
    return {month: dict(report[month]) for month in sorted(report)}


def write_summary(expenses: list[Expense], path: PathLike) -> None:
    totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    counts: defaultdict[str, int] = defaultdict(int)
    for e in expenses:
        totals[e.employee] += e.amount
        counts[e.employee] += 1

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["employee", "total", "count"])
        for emp in sorted(totals, key=lambda name: (-totals[name], name)):
            writer.writerow([emp, f"{totals[emp]:.2f}", counts[emp]])

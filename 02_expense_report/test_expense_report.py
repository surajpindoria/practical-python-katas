import csv
from datetime import date
from decimal import Decimal

import pytest

from expense_report import (
    Expense,
    load_expenses,
    monthly_report,
    totals_by_category,
    write_summary,
)

CSV_TEXT = """date,employee,category,amount
2024-01-05,Alice,Travel,120.50
2024-01-17, Bob ,meals ,45.00
2024-02-02,Alice,travel,80
2024-02-10,Carol,Office,not-a-number
2024-13-01,Bob,Meals,10.00
2024-02-28,Bob,Meals,15.25
,Alice,Office,5
2024-03-01,Dave,Office,-5.00
2024-03-02,,Office,5.00
"""


@pytest.fixture
def csv_path(tmp_path):
    p = tmp_path / "expenses.csv"
    p.write_text(CSV_TEXT)
    return p


@pytest.fixture
def loaded(csv_path):
    return load_expenses(csv_path)


def test_load_valid_rows(loaded):
    expenses, _ = loaded
    assert expenses == [
        Expense(date(2024, 1, 5), "Alice", "travel", Decimal("120.50")),
        Expense(date(2024, 1, 17), "Bob", "meals", Decimal("45.00")),
        Expense(date(2024, 2, 2), "Alice", "travel", Decimal("80")),
        Expense(date(2024, 2, 28), "Bob", "meals", Decimal("15.25")),
    ]


def test_amounts_are_decimal_not_float(loaded):
    expenses, _ = loaded
    assert all(type(e.amount) is Decimal for e in expenses)


def test_bad_line_numbers(loaded):
    _, bad = loaded
    assert bad == [5, 6, 8, 9, 10]


def test_accepts_str_path(csv_path):
    expenses, _ = load_expenses(str(csv_path))
    assert len(expenses) == 4


def test_header_only(tmp_path):
    p = tmp_path / "empty.csv"
    p.write_text("date,employee,category,amount\n")
    assert load_expenses(p) == ([], [])


def test_totals_by_category(loaded):
    expenses, _ = loaded
    assert totals_by_category(expenses) == {
        "travel": Decimal("200.50"),
        "meals": Decimal("60.25"),
    }


def test_totals_empty():
    assert totals_by_category([]) == {}


def test_monthly_report(loaded):
    expenses, _ = loaded
    report = monthly_report(expenses)
    assert report == {
        "2024-01": {"travel": Decimal("120.50"), "meals": Decimal("45.00")},
        "2024-02": {"travel": Decimal("80"), "meals": Decimal("15.25")},
    }


def test_monthly_report_is_chronological():
    expenses = [
        Expense(date(2024, 3, 1), "A", "x", Decimal("1")),
        Expense(date(2023, 12, 1), "A", "x", Decimal("1")),
        Expense(date(2024, 1, 1), "A", "x", Decimal("1")),
        Expense(date(2024, 3, 9), "A", "y", Decimal("2")),
    ]
    report = monthly_report(expenses)
    assert list(report) == ["2023-12", "2024-01", "2024-03"]
    assert report["2024-03"] == {"x": Decimal("1"), "y": Decimal("2")}


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.reader(f))


def test_write_summary(loaded, tmp_path):
    expenses, _ = loaded
    out = tmp_path / "summary.csv"
    write_summary(expenses, out)
    assert _read_csv(out) == [
        ["employee", "total", "count"],
        ["Alice", "200.50", "2"],
        ["Bob", "60.25", "2"],
    ]


def test_write_summary_tiebreak_and_formatting(tmp_path):
    expenses = [
        Expense(date(2024, 1, 1), "Zed", "x", Decimal("10")),
        Expense(date(2024, 1, 1), "Amy", "x", Decimal("7.5")),
        Expense(date(2024, 1, 2), "Amy", "y", Decimal("2.5")),
        Expense(date(2024, 1, 3), "Bo", "x", Decimal("0.333")),
    ]
    out = tmp_path / "summary.csv"
    write_summary(expenses, str(out))
    assert _read_csv(out) == [
        ["employee", "total", "count"],
        ["Amy", "10.00", "2"],
        ["Zed", "10.00", "1"],
        ["Bo", "0.33", "1"],
    ]

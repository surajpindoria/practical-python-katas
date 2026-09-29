# 02 · Expense Report  (Easy)

**Skills:** `csv` module, file I/O, `dataclasses`, `Decimal`, grouping and sorting

You get a CSV export of employee expenses:

```csv
date,employee,category,amount
2024-01-05,Alice,Travel,120.50
2024-01-17,Bob,meals ,45.00
```

An `Expense` frozen dataclass is already defined in `expense_report.py`.

## Part 1 — `load_expenses(path) -> (expenses, bad_lines)`

- Read the CSV at `path`. The header row is always present.
- Strip whitespace from every field.
- `date` → `datetime.date` (ISO format `YYYY-MM-DD`)
- `employee` → `str` (must be non-empty)
- `category` → `str`, **lower-cased**
- `amount` → `Decimal` (must be `>= 0`)
- If a row is invalid (bad or empty date, bad or negative amount, empty employee),
  skip it and record its **file line number**. The header is line 1, so the first
  data row is line 2.
- Return `(list_of_expenses_in_file_order, list_of_bad_line_numbers)`.

## Part 2 — `totals_by_category(expenses) -> dict[str, Decimal]`

Total amount per category.

## Part 3 — `monthly_report(expenses) -> dict[str, dict[str, Decimal]]`

Group totals by month (`"YYYY-MM"`) and then by category. The outer dict must be
ordered chronologically.

## Part 4 — `write_summary(expenses, path)`

Write a CSV with the header `employee,total,count`: one row per employee, with
`total` formatted to exactly 2 decimal places. Sort rows by total descending,
then by employee name ascending.

```bash
pipenv run pytest 02_expense_report
```

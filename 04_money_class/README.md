# 04 · Money Value Object  (Medium)

**Skills:** dunder methods, operator overloading, immutability, `Decimal`, `NotImplemented`,
equality and hashing, custom exceptions

Implement an immutable `Money` value type. `CurrencyMismatchError` is already
defined for you.

## Construction — `Money(amount, currency="USD")`

- `amount` may be `str`, `int` or `Decimal`. Passing a **`float` raises `TypeError`**
  (because of precision). An unparseable string such as `"abc"` raises `ValueError`.
- `amount` is stored as a `Decimal` quantized to 2 dp with `ROUND_HALF_UP`,
  so `"1.005"` → `Decimal("1.01")`.
- `currency` must be 3 letters. It is normalized to upper case (`"usd"` → `"USD"`).
  Anything else raises `ValueError`.
- Instances are **immutable**: assigning to `.amount` or `.currency` raises `AttributeError`.

## Behaviour

| Operation                | Result                                                                   |
|--------------------------|--------------------------------------------------------------------------|
| `a + b`, `a - b`         | `Money`. Different currencies raise `CurrencyMismatchError`. A non-Money operand raises `TypeError` |
| `sum([a, b, c])`         | works (hint: `sum` starts from `0`)                                      |
| `a * n`, `n * a`         | `n` is `int` or `Decimal`; the result is rounded to 2 dp. A `float` or `Money` operand raises `TypeError` |
| `-a`                     | negated `Money`                                                          |
| `bool(a)`                | `False` if the amount is zero                                            |
| `a == b`                 | `True` only if amount **and** currency match. Comparing with a non-Money gives `False` |
| `hash(a)`                | equal objects have equal hashes, so they can be used in sets and as dict keys |
| `<`, `<=`, `>`, `>=`     | same currency only. Otherwise raise `CurrencyMismatchError`              |
| `repr(a)`                | `Money('12.50', 'USD')`                                                  |
| `str(a)`                 | `12.50 USD`                                                              |

## `allocate(ratios) -> list[Money]`

Split the money across integer `ratios` **without losing or inventing a cent**.
Each share is rounded down to the cent. Then the leftover cents are handed out
one at a time, starting from the first share.

```python
Money("10.00").allocate([1, 1, 1])  # [3.34, 3.33, 3.33]
Money("0.05").allocate([70, 30])    # [0.04, 0.01]
```

Raise `ValueError` if `ratios` is empty, contains a negative number, or sums to 0.

```bash
pipenv run pytest 04_money_class
```

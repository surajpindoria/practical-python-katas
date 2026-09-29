# 08 · Transactional Key-Value Store  (Medium–Hard)

**Skills:** class design, internal data structures, sentinels, nested state,
context managers, custom exceptions, dunder methods

This is a very common "practical" interview question. Build an in-memory
key-value store that supports **nested transactions**.

## API — `TransactionalStore`

| method                   | behaviour                                                                  |
|--------------------------|----------------------------------------------------------------------------|
| `set(key, value)`        | store a value. **Any** value is allowed, including `None`                 |
| `get(key, default=None)` | return the value, or `default` if the key is absent                       |
| `delete(key)`            | remove a key. Raise `KeyError` if it's absent                             |
| `count(value)`           | number of keys currently mapped to a value equal to `value`               |
| `keys()`                 | **sorted** list of the currently visible keys (keys are strings)          |
| `len(store)`             | number of visible keys                                                    |
| `key in store`           | membership                                                                |
| `begin()`                | open a new (possibly nested) transaction                                  |
| `commit()`               | merge the **innermost** transaction into its parent, or into the main store if it is the outermost |
| `rollback()`             | discard the **innermost** transaction                                     |
| `depth`                  | property: number of open transactions                                     |
| `transaction()`          | context manager: `begin()` on enter. On a clean exit `commit()`. On an exception `rollback()` and re-raise |

- Reads always see the effect of every open transaction, innermost first.
- `commit()` / `rollback()` with no open transaction raise `NoTransactionError`
  (already defined for you, a subclass of `RuntimeError`).
- A key deleted inside a transaction must be invisible until that transaction is
  rolled back.

**Bonus (not tested):** can you make `rollback()` cost proportional to the number
of changes in that transaction, rather than to the size of the whole store?

```bash
pipenv run pytest 08_transactional_kv_store
```

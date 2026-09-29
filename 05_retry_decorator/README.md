# 05 · Retry Decorator  (Medium)

**Skills:** decorators (with and without arguments), closures, `functools.wraps`,
exception handling, dependency injection for testability

Write a `retry` decorator for flaky operations like network calls.

## Usage — both forms must work

```python
@retry
def fetch(): ...

@retry(max_attempts=5, exceptions=(ConnectionError,), delay=0.5, backoff=2)
def fetch(): ...
```

## Parameters (keyword-only when using the parenthesized form)

| name           | default        | meaning                                                              |
|----------------|----------------|----------------------------------------------------------------------|
| `max_attempts` | `3`            | total attempts, including the first. `< 1` → `ValueError` **at decoration time** |
| `exceptions`   | `(Exception,)` | a single exception class or a tuple of them. Only these trigger a retry |
| `delay`        | `0.0`          | wait before the 2nd attempt                                          |
| `backoff`      | `2.0`          | multiply the wait by this after each retry                           |
| `max_delay`    | `None`         | cap on any single wait (`None` = no cap)                             |
| `sleep`        | `time.sleep`   | function used to wait (injected in the tests so they run instantly)  |
| `on_retry`     | `None`         | if given, called as `on_retry(attempt_number, exception)` right **before** each sleep. `attempt_number` is the attempt that just failed, starting at 1 |

## Behaviour

- Pass `*args` and `**kwargs` through, and return the function's result.
- Between each pair of attempts, call `sleep(wait)` exactly once. The waits for
  `delay=1, backoff=2` are `1, 2, 4, ...`
- An exception that is **not** in `exceptions` propagates immediately with no retry.
- When all attempts fail, re-raise the **last** exception (the original object,
  not a wrapper).
- Preserve the wrapped function's metadata (`__name__`, `__doc__`, `__wrapped__`).
- Each call starts fresh. There is no shared attempt counter between calls.

```bash
pipenv run pytest 05_retry_decorator
```

# 10 · Async Concurrent Fetcher  (Hard)

**Skills:** `asyncio` (`TaskGroup`, `Semaphore`, `asyncio.timeout`, `wait`, cancellation),
error isolation, retries, dataclasses

`fetch` is always an **async callable** `await fetch(url) -> value` that may raise.
The tests use fake fetchers, so no real network access is needed.

`FetchResult` and `AllFailedError` are already defined for you.

## Part 1 — `async fetch_all(urls, fetch, max_concurrency=5, timeout=None, retries=0)`

Return `dict[url, FetchResult]`.

- **Never** have more than `max_concurrency` calls to `fetch` in flight at once.
  (The tests also check that you actually *reach* that level of concurrency, so
  running them one at a time will fail.)
- `timeout` (seconds, per attempt): an attempt that runs longer fails with
  the built-in `TimeoutError`. (Since Python 3.11, `asyncio.TimeoutError` is just an
  alias for it. Try the `async with asyncio.timeout(...)` context manager.)
- `retries`: extra attempts made after a failed attempt (any `Exception`,
  including a timeout). `FetchResult.attempts` records how many attempts were made.
- One URL failing must **not** affect the others.
- A duplicate URL is fetched only once.
- The returned dict is in **input order** (first occurrence).
- `max_concurrency < 1` → `ValueError`.

`FetchResult(url, ok, value=None, error=None, attempts=0)`. On success `ok=True`
and `value` is set. On failure `ok=False` and `error` is the **last** exception.

## Part 2 — `async first_successful(urls, fetch)`

Fetch every URL concurrently and return `(url, value)` for the **first one to
succeed**.

- As soon as one succeeds, **cancel** every fetch that's still running, and wait
  for the cancellations to finish before returning.
- Ignore failures unless *everything* fails. In that case raise
  `AllFailedError` with `.errors` = `{url: exception}`.
- An empty `urls` raises `ValueError`.

```bash
pipenv run pytest 10_async_fetcher
```

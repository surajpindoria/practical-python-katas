# 09 · Rate Limiters  (Hard)

**Skills:** class design, injectable clocks for deterministic tests, `collections.deque`,
`threading.Lock`, floating-point care, input validation

Build the two classic rate-limiting algorithms. Both take a `clock` callable that
returns the current time in seconds (default `time.monotonic`). The tests pass a
fake clock, so **never call `time` directly**. Always use `self.clock()` or
whatever you store it as.

## Part 1 — `SlidingWindowRateLimiter(max_requests, window_seconds, clock=time.monotonic)`

Allow at most `max_requests` per `key` within any rolling window of `window_seconds`.

- `allow(key) -> bool`: if the request is allowed, **record it** and return `True`.
  Otherwise return `False`. Denied requests are **not** recorded.
- A request made at time `t` counts against the limit while `now - t < window_seconds`.
  At exactly `t + window_seconds` it has expired.
- `remaining(key) -> int`: requests still available right now. It doesn't consume one.
- `retry_after(key) -> float`: seconds until the next request would be allowed.
  Return `0.0` if a request is allowed now.
- Each key is independent.
- `max_requests < 1` or `window_seconds <= 0` → `ValueError`.
- It must be **thread-safe**: concurrent `allow()` calls must never let more than
  `max_requests` through.

## Part 2 — `TokenBucket(capacity, refill_rate, clock=time.monotonic)`

- The bucket starts **full** (`capacity` tokens) and refills continuously at
  `refill_rate` tokens per second, never going above `capacity`.
- `consume(tokens=1) -> bool`: if enough tokens are available, take them and return
  `True`. Otherwise return `False` and take **nothing**.
- `tokens` (property): current token count as a float, after applying any refill.
- `consume(n)` with `n <= 0` or `n > capacity` raises `ValueError`.
- `capacity <= 0` or `refill_rate <= 0` raises `ValueError`.
- It must be thread-safe.

```bash
pipenv run pytest 09_rate_limiter
```

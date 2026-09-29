"""09 - Rate Limiters. See README.md for the full specification."""
import time
from collections.abc import Callable, Hashable

type Clock = Callable[[], float]


class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int, window_seconds: float, clock: Clock = time.monotonic) -> None:
        raise NotImplementedError

    def allow(self, key: Hashable) -> bool:
        raise NotImplementedError

    def remaining(self, key: Hashable) -> int:
        raise NotImplementedError

    def retry_after(self, key: Hashable) -> float:
        raise NotImplementedError


class TokenBucket:
    def __init__(self, capacity: float, refill_rate: float, clock: Clock = time.monotonic) -> None:
        raise NotImplementedError

    @property
    def tokens(self) -> float:
        raise NotImplementedError

    def consume(self, tokens: float = 1) -> bool:
        raise NotImplementedError

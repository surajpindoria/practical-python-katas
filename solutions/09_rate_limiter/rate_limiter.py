"""09 - Rate Limiters: reference solution."""
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable, Hashable

type Clock = Callable[[], float]


class SlidingWindowRateLimiter:
    """Keeps a deque of accepted request timestamps for each key (oldest on the left)."""

    def __init__(self, max_requests: int, window_seconds: float, clock: Clock = time.monotonic) -> None:
        if max_requests < 1:
            raise ValueError("max_requests must be >= 1")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")
        self.max_requests = max_requests
        self.window = window_seconds
        self.clock = clock
        self._hits: defaultdict[Hashable, deque[float]] = defaultdict(deque)
        # The check-then-append in allow() must be atomic, or two threads could
        # both see "one slot left" and both take it.
        self._lock = threading.Lock()

    def _prune(self, key: Hashable, now: float) -> deque[float]:
        hits = self._hits[key]
        while hits and now - hits[0] >= self.window:  # expired at exactly t + window
            hits.popleft()
        return hits

    def allow(self, key: Hashable) -> bool:
        with self._lock:
            now = self.clock()
            hits = self._prune(key, now)
            if len(hits) < self.max_requests:
                hits.append(now)
                return True
            return False

    def remaining(self, key: Hashable) -> int:
        with self._lock:
            return self.max_requests - len(self._prune(key, self.clock()))

    def retry_after(self, key: Hashable) -> float:
        with self._lock:
            now = self.clock()
            hits = self._prune(key, now)
            if len(hits) < self.max_requests:
                return 0.0
            return float(hits[0] + self.window - now)  # when the oldest request expires


class TokenBucket:
    """Refills lazily: tokens are recalculated from the elapsed time on each access, with no background thread."""

    def __init__(self, capacity: float, refill_rate: float, clock: Clock = time.monotonic) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be > 0")
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.clock = clock
        self._tokens = float(capacity)
        self._last = clock()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = self.clock()
        self._tokens = min(self.capacity, self._tokens + (now - self._last) * self.refill_rate)
        self._last = now

    @property
    def tokens(self) -> float:
        with self._lock:
            self._refill()
            return self._tokens

    def consume(self, tokens: float = 1) -> bool:
        if tokens <= 0 or tokens > self.capacity:
            raise ValueError("tokens must be in (0, capacity]")
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False

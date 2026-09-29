import threading

import pytest

from rate_limiter import SlidingWindowRateLimiter, TokenBucket


class FakeClock:
    def __init__(self, start=0.0):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture
def clock():
    return FakeClock()


# ------------------------------------------------------------ sliding window

def test_allows_up_to_limit(clock):
    rl = SlidingWindowRateLimiter(3, 10, clock=clock)
    assert [rl.allow("u") for _ in range(4)] == [True, True, True, False]


def test_window_expiry_boundary(clock):
    rl = SlidingWindowRateLimiter(3, 10, clock=clock)
    for _ in range(3):
        assert rl.allow("u")
        clock.advance(1)  # requests at t=0, 1, 2
    clock.now = 9.999
    assert not rl.allow("u")
    clock.now = 10.0  # the t=0 request expires exactly now
    assert rl.allow("u")
    assert not rl.allow("u")
    clock.now = 11.0
    assert rl.allow("u")


def test_denied_requests_are_not_recorded(clock):
    rl = SlidingWindowRateLimiter(1, 10, clock=clock)
    assert rl.allow("u")
    for t in range(1, 10):
        clock.now = t
        assert not rl.allow("u")
    clock.now = 10
    assert rl.allow("u")


def test_keys_are_independent(clock):
    rl = SlidingWindowRateLimiter(1, 10, clock=clock)
    assert rl.allow("alice")
    assert rl.allow("bob")
    assert not rl.allow("alice")


def test_remaining_does_not_consume(clock):
    rl = SlidingWindowRateLimiter(3, 10, clock=clock)
    assert rl.remaining("u") == 3
    assert rl.remaining("u") == 3
    rl.allow("u")
    assert rl.remaining("u") == 2
    clock.advance(10)
    assert rl.remaining("u") == 3


def test_retry_after(clock):
    rl = SlidingWindowRateLimiter(3, 10, clock=clock)
    assert rl.retry_after("u") == 0.0
    for t in (0, 1, 2):
        clock.now = t
        rl.allow("u")
    clock.now = 5
    assert rl.retry_after("u") == pytest.approx(5.0)
    clock.now = 10
    assert rl.retry_after("u") == 0.0


@pytest.mark.parametrize("args", [(0, 10), (-1, 10), (1, 0), (1, -5)])
def test_sliding_invalid_args(args):
    with pytest.raises(ValueError):
        SlidingWindowRateLimiter(*args)


def test_sliding_thread_safety():
    rl = SlidingWindowRateLimiter(100, 60)  # real clock
    results = []
    lock = threading.Lock()
    barrier = threading.Barrier(20)

    def worker():
        barrier.wait()
        local = [rl.allow("shared") for _ in range(25)]
        with lock:
            results.extend(local)

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sum(results) == 100


# ---------------------------------------------------------------- token bucket

def test_bucket_starts_full(clock):
    b = TokenBucket(5, 1, clock=clock)
    assert b.tokens == pytest.approx(5)
    assert [b.consume() for _ in range(6)] == [True] * 5 + [False]


def test_bucket_refills_continuously(clock):
    b = TokenBucket(10, 2, clock=clock)  # 2 tokens/sec
    for _ in range(10):
        b.consume()
    assert b.tokens == pytest.approx(0)
    clock.advance(0.25)
    assert b.tokens == pytest.approx(0.5)
    assert not b.consume()
    clock.advance(0.25)
    assert b.consume()
    assert b.tokens == pytest.approx(0)


def test_bucket_caps_at_capacity(clock):
    b = TokenBucket(3, 100, clock=clock)
    b.consume(3)
    clock.advance(60)
    assert b.tokens == pytest.approx(3)


def test_bucket_failed_consume_takes_nothing(clock):
    b = TokenBucket(5, 1, clock=clock)
    assert b.consume(4)
    assert not b.consume(3)
    assert b.tokens == pytest.approx(1)
    assert b.consume(1)


def test_bucket_multi_token_consume(clock):
    b = TokenBucket(10, 1, clock=clock)
    assert b.consume(7)
    clock.advance(4)
    assert b.consume(7)
    assert b.tokens == pytest.approx(0)


@pytest.mark.parametrize("n", [0, -1, 11])
def test_bucket_invalid_consume(clock, n):
    b = TokenBucket(10, 1, clock=clock)
    with pytest.raises(ValueError):
        b.consume(n)


@pytest.mark.parametrize("args", [(0, 1), (5, 0), (-1, 1), (5, -1)])
def test_bucket_invalid_args(args):
    with pytest.raises(ValueError):
        TokenBucket(*args)


def test_bucket_thread_safety():
    b = TokenBucket(50, 0.0001)  # effectively no refill during the test
    results = []
    lock = threading.Lock()
    barrier = threading.Barrier(10)

    def worker():
        barrier.wait()
        local = [b.consume() for _ in range(20)]
        with lock:
            results.extend(local)

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sum(results) == 50

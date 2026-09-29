import asyncio
import time
from collections import Counter

import pytest

from async_fetcher import AllFailedError, FetchResult, fetch_all, first_successful


class FakeFetcher:
    """Async fake. Behaviour per-URL is configured via the dicts below."""

    def __init__(self, delay=0.01, delays=None, fail=None, fail_times=None):
        self.delay = delay
        self.delays = delays or {}  # url -> seconds
        self.fail = fail or {}  # url -> exception to always raise
        self.fail_times = fail_times or {}  # url -> number of initial failures
        self.calls = Counter()
        self.in_flight = 0
        self.max_in_flight = 0
        self.cancelled = set()

    async def __call__(self, url):
        self.calls[url] += 1
        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        try:
            await asyncio.sleep(self.delays.get(url, self.delay))
            if url in self.fail:
                raise self.fail[url]
            if self.calls[url] <= self.fail_times.get(url, 0):
                raise ConnectionError(f"{url} attempt {self.calls[url]}")
            return f"content:{url}"
        except asyncio.CancelledError:
            self.cancelled.add(url)
            raise
        finally:
            self.in_flight -= 1


def run(coro):
    return asyncio.run(coro)


# ----------------------------------------------------------------- fetch_all

def test_fetch_all_success():
    f = FakeFetcher()
    urls = ["a", "b", "c"]
    results = run(fetch_all(urls, f))
    assert list(results) == urls
    assert results["a"] == FetchResult("a", ok=True, value="content:a", error=None, attempts=1)
    assert all(r.ok for r in results.values())


def test_fetch_all_respects_and_uses_concurrency_limit():
    f = FakeFetcher(delay=0.02)
    urls = [f"u{i}" for i in range(20)]
    run(fetch_all(urls, f, max_concurrency=4))
    assert f.max_in_flight == 4
    assert sum(f.calls.values()) == 20


def test_fetch_all_is_actually_concurrent():
    f = FakeFetcher(delay=0.1)
    urls = [f"u{i}" for i in range(10)]
    start = time.perf_counter()
    run(fetch_all(urls, f, max_concurrency=10))
    assert time.perf_counter() - start < 0.5  # sequential would take ~1s


def test_fetch_all_preserves_input_order_despite_completion_order():
    f = FakeFetcher(delays={"slow": 0.1, "fast": 0.0, "mid": 0.05})
    results = run(fetch_all(["slow", "fast", "mid"], f))
    assert list(results) == ["slow", "fast", "mid"]


def test_fetch_all_isolates_failures():
    boom = ValueError("boom")
    f = FakeFetcher(fail={"bad": boom})
    results = run(fetch_all(["ok1", "bad", "ok2"], f))
    assert results["ok1"].ok and results["ok2"].ok
    bad = results["bad"]
    assert not bad.ok
    assert bad.error is boom
    assert bad.value is None
    assert bad.attempts == 1


def test_fetch_all_timeout():
    f = FakeFetcher(delays={"slow": 2.0})
    start = time.perf_counter()
    results = run(fetch_all(["slow", "fast"], f, timeout=0.05))
    assert time.perf_counter() - start < 1.0
    assert isinstance(results["slow"].error, TimeoutError)
    assert results["fast"].ok


def test_fetch_all_retries_until_success():
    f = FakeFetcher(fail_times={"flaky": 2})
    results = run(fetch_all(["flaky"], f, retries=2))
    assert results["flaky"].ok
    assert results["flaky"].attempts == 3


def test_fetch_all_retries_exhausted():
    f = FakeFetcher(fail_times={"flaky": 5})
    results = run(fetch_all(["flaky"], f, retries=1))
    r = results["flaky"]
    assert not r.ok
    assert r.attempts == 2
    assert isinstance(r.error, ConnectionError)
    assert "attempt 2" in str(r.error)  # the *last* error


def test_fetch_all_retries_timeouts():
    f = FakeFetcher(delays={"slow": 2.0})
    results = run(fetch_all(["slow"], f, timeout=0.02, retries=2))
    assert results["slow"].attempts == 3
    assert f.calls["slow"] == 3


def test_fetch_all_dedupes():
    f = FakeFetcher()
    results = run(fetch_all(["a", "b", "a", "a"], f))
    assert list(results) == ["a", "b"]
    assert f.calls["a"] == 1


def test_fetch_all_empty():
    assert run(fetch_all([], FakeFetcher())) == {}


def test_fetch_all_invalid_concurrency():
    with pytest.raises(ValueError):
        run(fetch_all(["a"], FakeFetcher(), max_concurrency=0))


# ---------------------------------------------------------- first_successful

def test_first_successful_returns_fastest_success_and_cancels_rest():
    f = FakeFetcher(
        delays={"fail-fast": 0.0, "medium": 0.05, "slow1": 2.0, "slow2": 2.0},
        fail={"fail-fast": RuntimeError("nope")},
    )
    start = time.perf_counter()
    result = run(first_successful(["slow1", "fail-fast", "medium", "slow2"], f))
    assert result == ("medium", "content:medium")
    assert time.perf_counter() - start < 1.0
    assert f.cancelled == {"slow1", "slow2"}
    assert f.in_flight == 0


def test_first_successful_all_fail():
    e1, e2 = ValueError("1"), KeyError("2")
    f = FakeFetcher(fail={"a": e1, "b": e2})
    with pytest.raises(AllFailedError) as info:
        run(first_successful(["a", "b"], f))
    assert info.value.errors == {"a": e1, "b": e2}


def test_first_successful_empty():
    with pytest.raises(ValueError):
        run(first_successful([], FakeFetcher()))

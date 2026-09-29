import pytest

from retry import retry


class Flaky:
    """Callable that raises `exc_type` for the first `fail_times` calls."""

    def __init__(self, fail_times, exc_type=ValueError, result="ok"):
        self.fail_times = fail_times
        self.exc_type = exc_type
        self.result = result
        self.calls = 0
        self.raised = []

    def __call__(self, *args, **kwargs):
        self.calls += 1
        if self.calls <= self.fail_times:
            exc = self.exc_type(f"failure {self.calls}")
            self.raised.append(exc)
            raise exc
        return self.result


@pytest.fixture
def sleeps():
    return []


def test_success_first_try_no_sleep(sleeps):
    f = Flaky(0)
    wrapped = retry(max_attempts=3, sleep=sleeps.append)(f)
    assert wrapped() == "ok"
    assert f.calls == 1
    assert sleeps == []


def test_eventual_success_with_backoff(sleeps):
    f = Flaky(2)
    wrapped = retry(max_attempts=3, delay=1.0, backoff=2.0, sleep=sleeps.append)(f)
    assert wrapped() == "ok"
    assert f.calls == 3
    assert sleeps == [1.0, 2.0]


def test_exhausted_reraises_last_exception(sleeps):
    f = Flaky(10)
    wrapped = retry(max_attempts=4, sleep=sleeps.append)(f)
    with pytest.raises(ValueError) as info:
        wrapped()
    assert info.value is f.raised[-1]
    assert f.calls == 4
    assert len(sleeps) == 3


def test_max_delay_caps_waits(sleeps):
    f = Flaky(10)
    wrapped = retry(max_attempts=4, delay=1, backoff=10, max_delay=5, sleep=sleeps.append)(f)
    with pytest.raises(ValueError):
        wrapped()
    assert sleeps == [1, 5, 5]


def test_non_matching_exception_propagates_immediately(sleeps):
    f = Flaky(5, exc_type=KeyError)
    wrapped = retry(max_attempts=5, exceptions=(ValueError,), sleep=sleeps.append)(f)
    with pytest.raises(KeyError):
        wrapped()
    assert f.calls == 1
    assert sleeps == []


def test_single_exception_class_accepted(sleeps):
    f = Flaky(2, exc_type=ConnectionError)
    wrapped = retry(exceptions=ConnectionError, sleep=sleeps.append)(f)
    assert wrapped() == "ok"


def test_exception_subclasses_are_retried(sleeps):
    f = Flaky(1, exc_type=ConnectionResetError)  # subclass of ConnectionError
    wrapped = retry(exceptions=(ConnectionError,), sleep=sleeps.append)(f)
    assert wrapped() == "ok"


def test_on_retry_callback(sleeps):
    events = []
    f = Flaky(2)
    wrapped = retry(
        max_attempts=5,
        sleep=lambda s: events.append(("sleep", s)),
        delay=0.5,
        on_retry=lambda n, e: events.append(("retry", n, str(e))),
    )(f)
    wrapped()
    assert events == [
        ("retry", 1, "failure 1"),
        ("sleep", 0.5),
        ("retry", 2, "failure 2"),
        ("sleep", 1.0),
    ]


def test_args_and_kwargs_passed_through(sleeps):
    @retry(sleep=sleeps.append)
    def add(a, b, *, scale=1):
        return (a + b) * scale

    assert add(2, 3, scale=10) == 50


def test_bare_decorator_form():
    calls = {"n": 0}

    @retry
    def sometimes():
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("boom")
        return calls["n"]

    assert sometimes() == 3


def test_bare_decorator_default_is_three_attempts():
    calls = {"n": 0}

    @retry
    def always_fails():
        calls["n"] += 1
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        always_fails()
    assert calls["n"] == 3


def test_metadata_preserved():
    def original(x):
        """Docstring here."""
        return x

    for wrapped in (retry(original), retry(max_attempts=2)(original)):
        assert wrapped.__name__ == "original"
        assert wrapped.__doc__ == "Docstring here."
        assert wrapped.__wrapped__ is original


def test_invalid_max_attempts_at_decoration_time():
    with pytest.raises(ValueError):
        retry(max_attempts=0)


def test_each_call_is_independent(sleeps):
    state = {"n": 0}

    @retry(max_attempts=2, sleep=sleeps.append)
    def fails_odd_calls():
        state["n"] += 1
        if state["n"] % 2 == 1:
            raise ValueError
        return state["n"]

    assert fails_odd_calls() == 2
    assert fails_odd_calls() == 4

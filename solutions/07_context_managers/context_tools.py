"""07 - Context Managers: reference solution."""
import os
import tempfile
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import IO, Self


@contextmanager
def atomic_write(path: str | Path, mode: str = "w", encoding: str = "utf-8") -> Iterator[IO]:
    if mode not in ("w", "wb"):
        raise ValueError(f"unsupported mode {mode!r}")
    path = os.fspath(path)
    # The temp file must be in the same directory (same filesystem) for os.replace to be atomic.
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)), prefix=".tmp-")
    try:
        kwargs = {} if mode == "wb" else {"encoding": encoding}
        with os.fdopen(fd, mode, **kwargs) as f:
            yield f  # an exception in the with-block is re-raised here
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


@contextmanager
def temp_env(**overrides: str | None) -> Iterator[None]:
    # Validate everything before touching os.environ, so a TypeError changes nothing.
    for name, value in overrides.items():
        if value is not None and not isinstance(value, str):
            raise TypeError(f"{name} must be str or None, got {type(value).__name__}")

    saved = {name: os.environ.get(name) for name in overrides}  # None = didn't exist
    try:
        for name, value in overrides.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        yield
    finally:  # runs on success *and* on exception
        for name, value in saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


class Timer:
    def __init__(self, clock: Callable[[], float] = time.perf_counter) -> None:
        self._clock = clock
        self._start: float | None = None
        self.elapsed: float | None = None

    def __enter__(self) -> Self:
        self._start = self._clock()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.elapsed = self._clock() - self._start
        return False  # a truthy return value would suppress the exception

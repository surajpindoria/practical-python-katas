"""07 - Context Managers. See README.md for the full specification."""
import time
from collections.abc import Callable
from pathlib import Path


def atomic_write(path: str | Path, mode: str = "w", encoding: str = "utf-8"):
    raise NotImplementedError


def temp_env(**overrides: str | None):
    raise NotImplementedError


class Timer:
    def __init__(self, clock: Callable[[], float] = time.perf_counter) -> None:
        raise NotImplementedError

"""06 - Lazy Iterators & Pagination. See README.md for the full specification."""
from collections.abc import Callable, Iterable, Iterator
from typing import Any


def iter_items(
    fetch_page: Callable[[str | None], dict], max_pages: int | None = None
) -> Iterator[Any]:
    raise NotImplementedError


def batched[T](iterable: Iterable[T], n: int) -> Iterator[list[T]]:
    raise NotImplementedError


def take[T](iterable: Iterable[T], n: int) -> list[T]:
    raise NotImplementedError


def dedupe[T](iterable: Iterable[T], key: Callable[[T], Any] | None = None) -> Iterator[T]:
    raise NotImplementedError


def sliding_window[T](iterable: Iterable[T], n: int) -> Iterator[tuple[T, ...]]:
    raise NotImplementedError

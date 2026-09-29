"""06 - Lazy Iterators & Pagination: reference solution."""
from collections import deque
from collections.abc import Callable, Iterable, Iterator
from itertools import islice
from typing import Any


def iter_items(
    fetch_page: Callable[[str | None], dict], max_pages: int | None = None
) -> Iterator[Any]:
    # A generator function: none of this body runs until the first next(),
    # and it pauses at each yield, so pages are fetched only when needed.
    cursor: str | None = None
    seen: set[str] = set()
    pages = 0
    while max_pages is None or pages < max_pages:
        page = fetch_page(cursor)
        pages += 1
        yield from page["items"]
        cursor = page["next_cursor"]
        if cursor is None:
            return
        if cursor in seen:
            raise RuntimeError(f"cursor {cursor!r} repeated; the API would loop forever")
        seen.add(cursor)


def batched[T](iterable: Iterable[T], n: int) -> Iterator[list[T]]:
    # Stdlib alternative (3.12+): map(list, itertools.batched(iterable, n))
    if n < 1:
        raise ValueError("n must be >= 1")
    it = iter(iterable)  # a single shared iterator, so each islice continues where the last stopped
    while batch := list(islice(it, n)):
        yield batch


def take[T](iterable: Iterable[T], n: int) -> list[T]:
    # islice stops after exactly n items, so it never over-consumes.
    return list(islice(iterable, n))


def dedupe[T](iterable: Iterable[T], key: Callable[[T], Any] | None = None) -> Iterator[T]:
    seen: set[Any] = set()
    for item in iterable:
        k = item if key is None else key(item)
        if k not in seen:
            seen.add(k)
            yield item


def sliding_window[T](iterable: Iterable[T], n: int) -> Iterator[tuple[T, ...]]:
    # For n == 2, itertools.pairwise (3.10+) does the same thing.
    if n < 1:
        raise ValueError("n must be >= 1")
    it = iter(iterable)
    window = deque(islice(it, n - 1), maxlen=n)  # maxlen drops the oldest item automatically
    for item in it:
        window.append(item)
        yield tuple(window)

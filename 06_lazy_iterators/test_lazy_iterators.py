import itertools

import pytest

from lazy_iterators import batched, dedupe, iter_items, sliding_window, take


class FakeAPI:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def __call__(self, cursor):
        self.calls.append(cursor)
        idx = 0 if cursor is None else int(cursor)
        nxt = str(idx + 1) if idx + 1 < len(self.pages) else None
        return {"items": list(self.pages[idx]), "next_cursor": nxt}


# ---------------------------------------------------------------- iter_items

def test_iter_items_all():
    api = FakeAPI([[1, 2, 3], [4, 5], [6]])
    assert list(iter_items(api)) == [1, 2, 3, 4, 5, 6]
    assert api.calls == [None, "1", "2"]


def test_iter_items_is_lazy_before_first_next():
    api = FakeAPI([[1]])
    gen = iter_items(api)
    assert api.calls == []
    assert iter(gen) is gen  # it's an iterator
    next(gen)
    assert api.calls == [None]


def test_iter_items_does_not_prefetch_next_page():
    api = FakeAPI([[1, 2, 3], [4, 5]])
    gen = iter_items(api)
    assert [next(gen), next(gen), next(gen)] == [1, 2, 3]
    assert api.calls == [None]
    assert next(gen) == 4
    assert api.calls == [None, "1"]


def test_iter_items_skips_empty_pages():
    api = FakeAPI([[1], [], [], [2]])
    assert list(iter_items(api)) == [1, 2]


def test_iter_items_all_empty():
    assert list(iter_items(FakeAPI([[]]))) == []


def test_iter_items_detects_cursor_loop():
    def looping(cursor):
        return {"items": [cursor], "next_cursor": "same"}

    gen = iter_items(looping)
    with pytest.raises(RuntimeError):
        list(gen)


def test_iter_items_max_pages():
    api = FakeAPI([[1, 2], [3], [4]])
    assert list(iter_items(api, max_pages=2)) == [1, 2, 3]
    assert api.calls == [None, "1"]


# ------------------------------------------------------------------- batched

def test_batched():
    assert list(batched(range(7), 3)) == [[0, 1, 2], [3, 4, 5], [6]]
    assert list(batched([], 3)) == []
    assert list(batched("ab", 5)) == [["a", "b"]]


def test_batched_infinite():
    gen = batched(itertools.count(), 2)
    assert next(gen) == [0, 1]
    assert next(gen) == [2, 3]


def test_batched_invalid():
    with pytest.raises(ValueError):
        list(batched([1, 2], 0))


# ---------------------------------------------------------------------- take

def test_take():
    assert take(range(10), 3) == [0, 1, 2]
    assert take([1, 2], 5) == [1, 2]
    assert take([1, 2], 0) == []


def test_take_does_not_over_consume():
    it = iter([1, 2, 3, 4])
    assert take(it, 2) == [1, 2]
    assert next(it) == 3


def test_take_infinite():
    assert take(itertools.count(10), 3) == [10, 11, 12]


# -------------------------------------------------------------------- dedupe

def test_dedupe():
    assert list(dedupe([3, 1, 3, 2, 1, 4])) == [3, 1, 2, 4]


def test_dedupe_with_key():
    words = ["Apple", "apple", "Banana", "APPLE", "banana", "cherry"]
    assert list(dedupe(words, key=str.lower)) == ["Apple", "Banana", "cherry"]


def test_dedupe_lazy_on_infinite():
    stream = (i % 5 for i in itertools.count())  # 0,1,2,3,4,0,1,...
    assert take(dedupe(stream), 5) == [0, 1, 2, 3, 4]


# ------------------------------------------------------------ sliding_window

def test_sliding_window():
    assert list(sliding_window("abcd", 2)) == [("a", "b"), ("b", "c"), ("c", "d")]
    assert list(sliding_window([1, 2, 3], 3)) == [(1, 2, 3)]
    assert list(sliding_window([1, 2], 3)) == []


def test_sliding_window_infinite():
    assert take(sliding_window(itertools.count(), 3), 2) == [(0, 1, 2), (1, 2, 3)]


def test_sliding_window_invalid():
    with pytest.raises(ValueError):
        list(sliding_window([1], 0))

# 06 · Lazy Iterators & Pagination  (Medium)

**Skills:** generators, `yield` / `yield from`, the iterator protocol, `itertools`,
laziness, working with infinite streams

## `iter_items(fetch_page, max_pages=None)`

You're consuming a cursor-paginated API. `fetch_page(cursor)` returns
`{"items": [...], "next_cursor": str | None}`. The first call uses `cursor=None`,
and the stream ends when `next_cursor` is `None`.

- Return a **generator** that yields individual items.
- Be **lazy**. Don't call `fetch_page` at all until the first item is requested,
  and don't fetch page *N+1* until every item of page *N* has been consumed.
- Skip empty pages transparently.
- If the API returns a `next_cursor` that has **already been seen**, raise
  `RuntimeError`. Otherwise a buggy API would cause an infinite loop.
- Stop after `max_pages` pages if it is given.

## `batched(iterable, n)`

Yield lists of `n` items. The last list may be shorter. `n < 1` → `ValueError`.
It must work on infinite iterators.

> Python 3.12+ has `itertools.batched`, which yields *tuples*. Write your own first
> for practice, then compare. In an interview, knowing the stdlib version exists is
> worth mentioning.

## `take(iterable, n)`

Return a list of the first `n` items. Don't consume **more** than `n` items from
the underlying iterator.

## `dedupe(iterable, key=None)`

Lazily yield only the first occurrence of each item, or of each `key(item)` when
`key` is given. It must work on infinite iterators.

## `sliding_window(iterable, n)`

Yield overlapping tuples of length `n`: `sliding_window("abcd", 2)` → `('a','b'), ('b','c'), ('c','d')`.
If there are fewer than `n` items, yield nothing. `n < 1` → `ValueError`.

```bash
pipenv run pytest 06_lazy_iterators
```

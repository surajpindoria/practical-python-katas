"""08 - Transactional Key-Value Store: reference solution.

Design: committed data lives in `_data`. Each open transaction is a dict of
*changes only*, pushed onto a stack. A deletion is recorded as the `_DELETED`
sentinel, since we can't just remove the key: it may still exist in a lower layer.

- rollback is O(1): pop the top layer.
- commit is O(changes in that layer): replay it onto the layer below.
- get is O(depth): search the layers from the top down.
"""
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, Self

_DELETED = object()  # tombstone marking a key deleted inside a transaction
_MISSING = object()  # "not found", distinct from a stored None


class NoTransactionError(RuntimeError):
    """Raised by commit()/rollback() when no transaction is open."""


class TransactionalStore:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._txns: list[dict[str, Any]] = []

    # ---------------------------------------------------------------- helpers

    def _lookup(self, key: str) -> Any:
        for layer in reversed(self._txns):
            if key in layer:
                return layer[key]
        return self._data.get(key, _MISSING)

    def _apply(self, target: dict[str, Any], key: str, value: Any, *, base: bool) -> None:
        if value is _DELETED and base:
            target.pop(key, None)  # the committed store has no tombstones
        else:
            target[key] = value

    def _write(self, key: str, value: Any) -> None:
        if self._txns:
            self._txns[-1][key] = value
        else:
            self._apply(self._data, key, value, base=True)

    def _visible(self) -> dict[str, Any]:
        view = dict(self._data)
        for layer in self._txns:
            for k, v in layer.items():
                self._apply(view, k, v, base=True)
        return view

    # -------------------------------------------------------------------- API

    def set(self, key: str, value: Any) -> None:
        self._write(key, value)

    def get(self, key: str, default: Any = None) -> Any:
        value = self._lookup(key)
        return default if value is _MISSING or value is _DELETED else value

    def delete(self, key: str) -> None:
        if key not in self:
            raise KeyError(key)
        self._write(key, _DELETED)

    def count(self, value: Any) -> int:
        return sum(1 for v in self._visible().values() if v == value)

    def keys(self) -> list[str]:
        return sorted(self._visible())

    def __len__(self) -> int:
        return len(self._visible())

    def __contains__(self, key: object) -> bool:
        value = self._lookup(key)
        return value is not _MISSING and value is not _DELETED

    @property
    def depth(self) -> int:
        return len(self._txns)

    def begin(self) -> None:
        self._txns.append({})

    def commit(self) -> None:
        if not self._txns:
            raise NoTransactionError("no open transaction")
        layer = self._txns.pop()
        target = self._txns[-1] if self._txns else self._data
        for k, v in layer.items():
            # Tombstones stay as tombstones in a parent transaction.
            self._apply(target, k, v, base=target is self._data)

    def rollback(self) -> None:
        if not self._txns:
            raise NoTransactionError("no open transaction")
        self._txns.pop()

    @contextmanager
    def transaction(self) -> Iterator[Self]:
        self.begin()
        try:
            yield self
        except BaseException:
            self.rollback()
            raise
        self.commit()

"""08 - Transactional Key-Value Store. See README.md for the full specification."""
from typing import Any


class NoTransactionError(RuntimeError):
    """Raised by commit()/rollback() when no transaction is open."""


class TransactionalStore:
    def __init__(self) -> None:
        raise NotImplementedError

    def set(self, key: str, value: Any) -> None:
        raise NotImplementedError

    def get(self, key: str, default: Any = None) -> Any:
        raise NotImplementedError

    def delete(self, key: str) -> None:
        raise NotImplementedError

    def count(self, value: Any) -> int:
        raise NotImplementedError

    def keys(self) -> list[str]:
        raise NotImplementedError

    def begin(self) -> None:
        raise NotImplementedError

    def commit(self) -> None:
        raise NotImplementedError

    def rollback(self) -> None:
        raise NotImplementedError

    # Also implement: depth (property), transaction() (context manager),
    # __len__, __contains__

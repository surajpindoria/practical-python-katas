"""10 - Async Concurrent Fetcher. See README.md for the full specification."""
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from typing import Any

type Fetch = Callable[[str], Awaitable[Any]]


@dataclass
class FetchResult:
    url: str
    ok: bool
    value: Any = None
    error: BaseException | None = None
    attempts: int = 0


class AllFailedError(Exception):
    def __init__(self, errors: dict[str, BaseException]) -> None:
        super().__init__(f"all {len(errors)} fetches failed")
        self.errors = errors


async def fetch_all(
    urls: Iterable[str],
    fetch: Fetch,
    max_concurrency: int = 5,
    timeout: float | None = None,
    retries: int = 0,
) -> dict[str, FetchResult]:
    raise NotImplementedError


async def first_successful(urls: Iterable[str], fetch: Fetch) -> tuple[str, Any]:
    raise NotImplementedError

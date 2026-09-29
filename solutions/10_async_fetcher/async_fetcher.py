"""10 - Async Concurrent Fetcher: reference solution."""
import asyncio
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
    if max_concurrency < 1:
        raise ValueError("max_concurrency must be >= 1")
    unique = list(dict.fromkeys(urls))  # de-duplicate while keeping first-seen order
    sem = asyncio.Semaphore(max_concurrency)

    async def fetch_one(url: str) -> FetchResult:
        error: BaseException | None = None
        for attempt in range(1, retries + 2):
            try:
                # Hold the semaphore only while fetching, so a URL waiting to
                # retry doesn't block a slot. asyncio.timeout(None) means no limit.
                async with sem, asyncio.timeout(timeout):
                    value = await fetch(url)
                return FetchResult(url, True, value=value, attempts=attempt)
            except Exception as exc:  # not BaseException: let CancelledError through
                error = exc
        return FetchResult(url, False, error=error, attempts=retries + 1)

    # fetch_one never raises (errors become FetchResults), so the TaskGroup
    # never cancels its siblings.
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_one(u)) for u in unique]
    return {u: t.result() for u, t in zip(unique, tasks)}


async def first_successful(urls: Iterable[str], fetch: Fetch) -> tuple[str, Any]:
    unique = list(dict.fromkeys(urls))
    if not unique:
        raise ValueError("urls must not be empty")

    tasks = {asyncio.create_task(fetch(u)): u for u in unique}
    pending = set(tasks)
    errors: dict[str, BaseException] = {}
    try:
        while pending:
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                if task.exception() is None:
                    return tasks[task], task.result()
                errors[tasks[task]] = task.exception()
        raise AllFailedError({u: errors[u] for u in unique})
    finally:
        # Runs on return, on raise and on outside cancellation: cancel the
        # leftovers, then wait for them so none outlive this call.
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)

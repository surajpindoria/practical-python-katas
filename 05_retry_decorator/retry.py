"""05 - Retry Decorator. See README.md for the full specification."""
import time
from collections.abc import Callable

type ExcTypes = type[BaseException] | tuple[type[BaseException], ...]


def retry(
    _func: Callable | None = None,
    *,
    max_attempts: int = 3,
    exceptions: ExcTypes = (Exception,),
    delay: float = 0.0,
    backoff: float = 2.0,
    max_delay: float | None = None,
    sleep: Callable[[float], None] = time.sleep,
    on_retry: Callable[[int, BaseException], None] | None = None,
):
    raise NotImplementedError

"""05 - Retry Decorator: reference solution."""
import functools
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
    # Validate here so bad config fails at decoration time, not on the first call.
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)  # copies __name__, __doc__ and sets __wrapped__
        def wrapper(*args, **kwargs):
            wait = delay  # local, so every call starts fresh
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:  # `except` accepts a class or a tuple of classes
                    if attempt == max_attempts:
                        raise  # a bare raise re-raises the original exception object
                    if on_retry is not None:
                        on_retry(attempt, exc)
                    sleep(wait if max_delay is None else min(wait, max_delay))
                    wait *= backoff

        return wrapper

    # @retry         -> Python calls retry(func), so _func is the function.
    # @retry(...)    -> _func is None, so return the decorator to be applied next.
    if _func is not None:
        return decorator(_func)
    return decorator

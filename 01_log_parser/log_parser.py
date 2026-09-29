"""01 - Log Parser. See README.md for the full specification."""
from collections.abc import Iterable


def parse_line(line: str) -> dict | None:
    """Parse a single access-log line into a dict, or return None if malformed."""
    raise NotImplementedError


def summarize(lines: Iterable[str], top_n: int = 3) -> dict:
    """Aggregate statistics over many log lines."""
    raise NotImplementedError

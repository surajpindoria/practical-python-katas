"""03 - Nested Dict Utilities. See README.md for the full specification."""
from typing import Any


def flatten(d: dict, sep: str = ".") -> dict:
    raise NotImplementedError


def unflatten(d: dict, sep: str = ".") -> dict:
    raise NotImplementedError


def deep_merge(base: dict, override: dict) -> dict:
    raise NotImplementedError


def get_path(d: dict, path: str, default: Any = None, sep: str = ".") -> Any:
    raise NotImplementedError

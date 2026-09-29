"""03 - Nested Dict Utilities: reference solution."""
from typing import Any

# A sentinel lets us tell "key missing" apart from "key present with value None".
_MISSING = object()


def flatten(d: dict, sep: str = ".") -> dict:
    out: dict[str, Any] = {}

    def walk(node: dict, prefix: str | None) -> None:
        for k, v in node.items():
            key = str(k) if prefix is None else f"{prefix}{sep}{k}"
            if isinstance(v, dict) and v:  # empty dicts are leaves
                walk(v, key)
            else:
                out[key] = v

    walk(d, None)
    return out


def unflatten(d: dict, sep: str = ".") -> dict:
    out: dict[str, Any] = {}
    for flat_key, value in d.items():
        *parents, last = flat_key.split(sep)
        node = out
        for part in parents:
            node = node.setdefault(part, {})
            if not isinstance(node, dict):  # e.g. "a" was already set to a leaf
                raise ValueError(f"conflicting key {flat_key!r}")
        if last in node:  # e.g. "a.b" already created "a" as a dict
            raise ValueError(f"conflicting key {flat_key!r}")
        node[last] = value
    return out


def deep_merge(base: dict, override: dict) -> dict:
    # Recursing on every dict (even with nothing to merge) copies it, so the
    # result never shares nested dicts with the inputs.
    result = {k: deep_merge(v, {}) if isinstance(v, dict) else v for k, v in base.items()}
    for k, v in override.items():
        if isinstance(v, dict):
            existing = result.get(k)
            result[k] = deep_merge(existing if isinstance(existing, dict) else {}, v)
        else:
            result[k] = v
    return result


def get_path(d: dict, path: str, default: Any = None, sep: str = ".") -> Any:
    node: Any = d
    for part in path.split(sep):
        if not isinstance(node, dict):
            return default
        node = node.get(part, _MISSING)
        if node is _MISSING:
            return default
    return node

# 03 · Nested Dict Utilities  (Easy–Medium)

**Skills:** recursion, dict manipulation, avoiding mutation of inputs, precise edge cases

This kind of helper shows up constantly in config and JSON handling code.

## `flatten(d, sep=".")`

```python
flatten({"a": {"b": 1, "c": {"d": 2}}, "e": 3})
# {"a.b": 1, "a.c.d": 2, "e": 3}
```

- Only dicts are recursed into. Lists and other values are leaves and are kept as-is.
- An **empty** nested dict is a leaf, so `{"a": {}}` → `{"a": {}}`.
- Non-string keys are converted with `str()`.
- Don't mutate the input.

## `unflatten(d, sep=".")`

This is the inverse of `flatten`:

```python
unflatten({"a.b": 1, "a.c": 2, "d": 3})
# {"a": {"b": 1, "c": 2}, "d": 3}
```

- Raise `ValueError` on conflicting keys such as `{"a": 1, "a.b": 2}`, regardless
  of the order they appear in.

## `deep_merge(base, override)`

Return a **new** dict in which `override` wins. When both sides have a dict at the
same key, merge them recursively. Otherwise the value from `override` replaces the
one in `base`. Neither input may be mutated, and the result must not share nested
dict objects with either input (mutating the result must never affect the inputs).

## `get_path(d, path, default=None, sep=".")`

`get_path(cfg, "db.primary.host")` walks the nested dict. It returns `default` if any
segment is missing or if it hits a non-dict along the way.

```bash
pipenv run pytest 03_nested_dicts
```

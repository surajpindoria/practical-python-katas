# 07 · Context Managers  (Medium)

**Skills:** `contextlib.contextmanager`, class-based `__enter__`/`__exit__`, `try/finally`,
filesystem operations (`os.replace`, `tempfile`), `os.environ`, exception safety

## `atomic_write(path, mode="w", encoding="utf-8")`

```python
with atomic_write("config.json") as f:
    f.write(data)
```

- Yield a writable file object for a **temporary file in the same directory** as
  `path`. The same directory is required so the final rename is atomic.
- On a clean exit, atomically replace `path` with the temp file (`os.replace`).
- If an exception happens inside the block, leave `path` **untouched**, delete the
  temp file, and let the exception propagate.
- The target must not change until the block exits successfully.
- Only `"w"` and `"wb"` are allowed. Any other mode raises `ValueError`, and
  `encoding` is ignored for `"wb"`.
- `path` may be a `str` or a `pathlib.Path`.

## `temp_env(**overrides)`

```python
with temp_env(API_URL="http://localhost", DEBUG=None):
    ...
```

- Set each variable in `os.environ`. A value of `None` means *unset it*.
- On exit, **restore the environment exactly**, even if an exception is raised.
  Variables that didn't exist before must be removed again.
- Every value must be a `str` or `None`. Otherwise raise `TypeError` **before
  changing anything**.

## `Timer`

```python
with Timer() as t:
    do_work()
print(t.elapsed)
```

- `Timer(clock=time.perf_counter)` takes an injectable clock.
- `__enter__` returns the timer itself.
- `elapsed` is `None` until the first block finishes. After that it is a float
  (seconds).
- It must not swallow exceptions, but it still records `elapsed` when one occurs.
- It is reusable: each `with` block re-measures.

```bash
pipenv run pytest 07_context_managers
```

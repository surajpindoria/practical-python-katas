# Practical Python Katas

Practical Python katas that test language fluency rather than algorithms.
Each folder contains:

- `README.md`: the spec. Read it carefully, since the tests check the edge cases it describes.
- `<module>.py`: the starter file with stubs. Replace each `raise NotImplementedError` with your code.
- `test_<module>.py`: automated tests. Try not to read these until you've finished a first pass.

| #  | Problem                                                  | Difficulty  | Main skills                                          |
|----|----------------------------------------------------------|-------------|------------------------------------------------------|
| 01 | [Log Parser](01_log_parser/README.md)                    | Easy        | regex, `datetime`, `Counter`, handling bad input     |
| 02 | [Expense Report](02_expense_report/README.md)            | Easy        | `csv`, file I/O, dataclasses, `Decimal`, sorting     |
| 03 | [Nested Dicts](03_nested_dicts/README.md)                | Easy–Med    | recursion, avoiding mutation, edge cases             |
| 04 | [Money Class](04_money_class/README.md)                  | Medium      | dunder methods, immutability, hashing, `NotImplemented` |
| 05 | [Retry Decorator](05_retry_decorator/README.md)          | Medium      | decorators with and without args, `functools.wraps`  |
| 06 | [Lazy Iterators](06_lazy_iterators/README.md)            | Medium      | generators, `itertools`, laziness                    |
| 07 | [Context Managers](07_context_managers/README.md)        | Medium      | `contextmanager`, `__enter__`/`__exit__`, atomic files |
| 08 | [Transactional KV Store](08_transactional_kv_store/README.md) | Med–Hard | class design, nested state, sentinels              |
| 09 | [Rate Limiters](09_rate_limiter/README.md)               | Hard        | injectable clocks, `deque`, `threading.Lock`         |
| 10 | [Async Fetcher](10_async_fetcher/README.md)              | Hard        | `asyncio`, semaphores, timeouts, cancellation        |

## Setup (one time)

You need **Python 3.14** and [pipenv](https://pipenv.pypa.io) installed. From the project
root, create the environment in a `.venv/` folder inside the project:

```bash
# macOS / Linux
PIPENV_VENV_IN_PROJECT=1 pipenv install --dev
```

```powershell
# Windows (PowerShell)
$env:PIPENV_VENV_IN_PROJECT = 1; pipenv install --dev
```

`PIPENV_VENV_IN_PROJECT` matters because the VS Code configurations below expect the
environment at `.venv/`. By default pipenv would put it somewhere else. Once `.venv/`
exists, pipenv finds it automatically, so you only need this the first time.

The starter files use modern syntax: `list[int]`, `X | None`, `type` aliases, and
generic functions like `def take[T](...)`. Feel free to use `match`, the walrus
operator, `itertools.batched` / `pairwise`, `asyncio.TaskGroup` and so on in your
solutions.

## Running tests

```bash
pipenv run pytest 04_money_class                 # one problem
pipenv run pytest 04_money_class -x              # stop at first failure
pipenv run pytest 04_money_class -k allocate     # only tests matching a name
pipenv run test                                  # everything
```

Or run `pipenv shell` once, and then just use `pytest ...`.

### Running tests from VS Code

Open the project's root folder in VS Code (File → Open Folder). You'll also
need Microsoft's Python extension.

The project includes `.vscode/launch.json`, so you can run tests from the **Run and Debug**
panel. Pick a configuration from the dropdown next to ▶, then click ▶ or press **F5**:

| Configuration                 | What it runs                                                          |
|-------------------------------|-----------------------------------------------------------------------|
| **Tests: current problem**    | Tests for the problem whose file is open in the editor. Open `04_money_class/money.py`, press F5, and the Money tests run |
| **Tests: choose problem…**    | Shows a list of the 10 problems to pick from                          |
| **Tests: all problems**       | Every test                                                            |
| **Solutions: choose problem…**| A problem's tests run against the reference solutions                 |

The tests run under the debugger, so breakpoints in your code (or the tests) will pause
execution. That makes it easy to step through a failing edge case. The **Testing**
panel (flask icon) also lists every test, with its own run and debug buttons.

## Reference solutions (spoilers)

[`solutions/`](solutions/README.md) has an annotated reference solution for every problem,
with the same folder names. Add `--solutions` to any test command to run the tests
against them instead of your code:

```bash
pipenv run pytest 04_money_class --solutions
```

## Suggested practice routine

1. Set a timer: about 20 minutes for Easy, 30–40 for Medium, and 45+ for Hard.
2. Read only the problem's `README.md`, then write your solution. Talk out loud as
   you would in the interview.
3. Run the tests, fix any failures, and note which edge cases you missed.
4. Review your code: is it idiomatic, with good names, type hints and no needless
   complexity?
5. A few days later, redo the problems you found hard from scratch.

## License

[MIT](LICENSE)

"""Adds a --solutions flag that runs the tests against solutions/ instead of your code.

    pipenv run pytest 04_money_class               # tests your money.py
    pipenv run pytest 04_money_class --solutions   # tests solutions/04_money_class/money.py
"""
import importlib.util
import sys
from pathlib import Path

SOLUTIONS_DIR = Path(__file__).parent / "solutions"


def pytest_addoption(parser):
    parser.addoption(
        "--solutions",
        action="store_true",
        help="run the tests against the reference solutions in solutions/",
    )


def pytest_configure(config):
    if not config.getoption("--solutions"):
        return
    # Test files do `from money import Money`. Preloading the reference modules
    # into sys.modules under those names makes the imports resolve to them.
    for path in sorted(SOLUTIONS_DIR.glob("*/*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[path.stem] = module  # register before exec: dataclasses look it up
        spec.loader.exec_module(module)


def pytest_report_header(config):
    if config.getoption("--solutions"):
        return "*** running against REFERENCE SOLUTIONS (solutions/) ***"

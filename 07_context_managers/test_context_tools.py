import os

import pytest

from context_tools import Timer, atomic_write, temp_env


# -------------------------------------------------------------- atomic_write

def test_atomic_write_creates_file(tmp_path):
    target = tmp_path / "out.txt"
    with atomic_write(target) as f:
        f.write("hello")
    assert target.read_text() == "hello"


def test_atomic_write_accepts_str_path(tmp_path):
    target = tmp_path / "out.txt"
    with atomic_write(str(target)) as f:
        f.write("hi")
    assert target.read_text() == "hi"


def test_atomic_write_replaces_existing(tmp_path):
    target = tmp_path / "out.txt"
    target.write_text("old")
    with atomic_write(target) as f:
        f.write("new")
    assert target.read_text() == "new"


def test_target_unchanged_until_exit(tmp_path):
    target = tmp_path / "out.txt"
    target.write_text("old")
    with atomic_write(target) as f:
        f.write("new")
        f.flush()
        assert target.read_text() == "old"


def test_temp_file_lives_in_same_directory(tmp_path):
    target = tmp_path / "out.txt"
    with atomic_write(target) as f:
        f.write("x")
        f.flush()
        entries = os.listdir(tmp_path)
        assert len(entries) == 1 and entries[0] != "out.txt"
    assert os.listdir(tmp_path) == ["out.txt"]


def test_exception_leaves_original_and_cleans_up(tmp_path):
    target = tmp_path / "out.txt"
    target.write_text("original")
    with pytest.raises(ZeroDivisionError):
        with atomic_write(target) as f:
            f.write("partial")
            1 / 0
    assert target.read_text() == "original"
    assert os.listdir(tmp_path) == ["out.txt"]


def test_exception_on_new_file_creates_nothing(tmp_path):
    class Boom(Exception):
        pass

    target = tmp_path / "new.txt"
    with pytest.raises(Boom):
        with atomic_write(target):
            raise Boom
    assert os.listdir(tmp_path) == []


def test_binary_mode(tmp_path):
    target = tmp_path / "blob.bin"
    with atomic_write(target, mode="wb") as f:
        f.write(b"\x00\x01\x02")
    assert target.read_bytes() == b"\x00\x01\x02"


def test_encoding(tmp_path):
    target = tmp_path / "u.txt"
    with atomic_write(target, encoding="utf-16") as f:
        f.write("héllo")
    assert target.read_text(encoding="utf-16") == "héllo"


@pytest.mark.parametrize("mode", ["a", "r", "w+", "ab"])
def test_invalid_mode(tmp_path, mode):
    with pytest.raises(ValueError):
        with atomic_write(tmp_path / "x", mode=mode):
            pass


# ------------------------------------------------------------------ temp_env

A, B, C = "CTX_TEST_VAR_A", "CTX_TEST_VAR_B", "CTX_TEST_VAR_C"


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in (A, B, C):
        monkeypatch.delenv(name, raising=False)


def test_temp_env_sets_and_removes_new_var():
    with temp_env(**{A: "1"}):
        assert os.environ[A] == "1"
    assert A not in os.environ


def test_temp_env_overrides_and_restores(monkeypatch):
    monkeypatch.setenv(A, "original")
    with temp_env(**{A: "temp"}):
        assert os.environ[A] == "temp"
    assert os.environ[A] == "original"


def test_temp_env_none_unsets_and_restores(monkeypatch):
    monkeypatch.setenv(A, "original")
    with temp_env(**{A: None, B: None}):
        assert A not in os.environ
        assert B not in os.environ
    assert os.environ[A] == "original"
    assert B not in os.environ


def test_temp_env_restores_on_exception(monkeypatch):
    monkeypatch.setenv(A, "original")
    with pytest.raises(KeyError):
        with temp_env(**{A: "temp", B: "new"}):
            raise KeyError
    assert os.environ[A] == "original"
    assert B not in os.environ


def test_temp_env_restores_changes_made_inside(monkeypatch):
    monkeypatch.setenv(A, "original")
    with temp_env(**{A: "temp"}):
        os.environ[A] = "changed-inside"
    assert os.environ[A] == "original"


def test_temp_env_nested():
    with temp_env(**{A: "outer"}):
        with temp_env(**{A: "inner", C: "c"}):
            assert os.environ[A] == "inner"
        assert os.environ[A] == "outer"
        assert C not in os.environ
    assert A not in os.environ


def test_temp_env_type_error_changes_nothing(monkeypatch):
    monkeypatch.setenv(A, "original")
    with pytest.raises(TypeError):
        with temp_env(**{A: "new", B: 123}):
            pass
    assert os.environ[A] == "original"
    assert B not in os.environ


# --------------------------------------------------------------------- Timer

def fake_clock(*values):
    it = iter(values)
    return lambda: next(it)


def test_timer_measures():
    with Timer(clock=fake_clock(10.0, 12.5)) as t:
        pass
    assert t.elapsed == 2.5


def test_timer_enter_returns_self():
    timer = Timer(clock=fake_clock(0, 1))
    with timer as t:
        assert t is timer


def test_timer_elapsed_none_before_finish():
    t = Timer(clock=fake_clock(0, 1))
    assert t.elapsed is None


def test_timer_does_not_swallow_but_records():
    t = Timer(clock=fake_clock(1.0, 4.0))
    with pytest.raises(ValueError):
        with t:
            raise ValueError
    assert t.elapsed == 3.0


def test_timer_reusable():
    t = Timer(clock=fake_clock(0.0, 1.0, 5.0, 5.5))
    with t:
        pass
    assert t.elapsed == 1.0
    with t:
        pass
    assert t.elapsed == 0.5


def test_timer_real_clock():
    with Timer() as t:
        sum(range(1000))
    assert isinstance(t.elapsed, float)
    assert t.elapsed >= 0

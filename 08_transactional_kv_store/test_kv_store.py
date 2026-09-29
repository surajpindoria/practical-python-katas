import pytest

from kv_store import NoTransactionError, TransactionalStore


@pytest.fixture
def store():
    return TransactionalStore()


# --------------------------------------------------------------------- basics

def test_set_get(store):
    store.set("a", 1)
    assert store.get("a") == 1
    assert store.get("missing") is None
    assert store.get("missing", "dflt") == "dflt"


def test_none_is_a_real_value(store):
    store.set("a", None)
    assert "a" in store
    assert store.get("a", "dflt") is None
    assert len(store) == 1


def test_overwrite(store):
    store.set("a", 1)
    store.set("a", 2)
    assert store.get("a") == 2
    assert len(store) == 1


def test_delete(store):
    store.set("a", 1)
    store.delete("a")
    assert "a" not in store
    with pytest.raises(KeyError):
        store.delete("a")


def test_count(store):
    store.set("a", 10)
    store.set("b", 10)
    store.set("c", 20)
    assert store.count(10) == 2
    assert store.count(99) == 0
    store.set("b", 20)
    assert store.count(10) == 1
    assert store.count(20) == 2


def test_keys_sorted_and_len(store):
    for k in ["c", "a", "b"]:
        store.set(k, k)
    assert store.keys() == ["a", "b", "c"]
    assert len(store) == 3


# --------------------------------------------------------------- transactions

def test_rollback_undoes_changes(store):
    store.set("a", 1)
    store.begin()
    store.set("a", 2)
    store.set("b", 3)
    assert store.get("a") == 2
    store.rollback()
    assert store.get("a") == 1
    assert "b" not in store


def test_commit_persists(store):
    store.begin()
    store.set("a", 1)
    store.commit()
    assert store.get("a") == 1
    assert store.depth == 0


def test_delete_inside_transaction_then_rollback(store):
    store.set("a", 1)
    store.begin()
    store.delete("a")
    assert "a" not in store
    assert store.get("a") is None
    assert store.keys() == []
    assert store.count(1) == 0
    with pytest.raises(KeyError):
        store.delete("a")
    store.rollback()
    assert store.get("a") == 1


def test_delete_then_set_in_same_transaction(store):
    store.set("a", 1)
    store.begin()
    store.delete("a")
    store.set("a", 2)
    store.commit()
    assert store.get("a") == 2


def test_nested_rollback_inner_only(store):
    store.set("a", 1)
    store.begin()
    store.set("a", 2)
    store.begin()
    store.set("a", 3)
    assert store.depth == 2
    store.rollback()
    assert store.get("a") == 2
    assert store.depth == 1
    store.rollback()
    assert store.get("a") == 1


def test_nested_commit_merges_into_parent(store):
    store.set("a", 1)
    store.begin()
    store.begin()
    store.set("a", 3)
    store.set("b", 4)
    store.commit()  # inner merged into outer
    assert store.depth == 1
    assert store.get("a") == 3
    store.rollback()  # discards the outer, including merged inner changes
    assert store.get("a") == 1
    assert "b" not in store


def test_nested_delete_merges(store):
    store.set("a", 1)
    store.begin()
    store.begin()
    store.delete("a")
    store.commit()
    assert "a" not in store
    store.commit()
    assert "a" not in store
    assert len(store) == 0


def test_count_and_len_see_transactions(store):
    store.set("a", 10)
    store.set("b", 10)
    store.begin()
    store.set("a", 20)
    store.set("c", 10)
    assert store.count(10) == 2
    assert store.count(20) == 1
    assert len(store) == 3
    store.rollback()
    assert store.count(10) == 2
    assert store.count(20) == 0
    assert len(store) == 2


def test_no_transaction_errors(store):
    assert issubclass(NoTransactionError, RuntimeError)
    with pytest.raises(NoTransactionError):
        store.commit()
    with pytest.raises(NoTransactionError):
        store.rollback()


# ------------------------------------------------------ transaction() context

def test_context_commit(store):
    with store.transaction():
        store.set("a", 1)
    assert store.get("a") == 1
    assert store.depth == 0


def test_context_rollback_on_error(store):
    store.set("a", 1)
    with pytest.raises(ValueError):
        with store.transaction():
            store.set("a", 2)
            raise ValueError("boom")
    assert store.get("a") == 1
    assert store.depth == 0


def test_context_nested(store):
    with store.transaction():
        store.set("a", 1)
        with pytest.raises(RuntimeError):
            with store.transaction():
                store.set("a", 2)
                store.set("b", 2)
                raise RuntimeError
        assert store.get("a") == 1
        assert "b" not in store
    assert store.get("a") == 1

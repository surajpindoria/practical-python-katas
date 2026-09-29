import copy

import pytest

from nested_dicts import deep_merge, flatten, get_path, unflatten

NESTED = {"a": {"b": 1, "c": {"d": 2}}, "e": 3}


# ------------------------------------------------------------------- flatten

def test_flatten_basic():
    assert flatten(NESTED) == {"a.b": 1, "a.c.d": 2, "e": 3}


def test_flatten_custom_sep():
    assert flatten(NESTED, sep="/") == {"a/b": 1, "a/c/d": 2, "e": 3}


def test_flatten_keeps_empty_dict_as_leaf():
    assert flatten({"a": {}, "b": {"c": {}}}) == {"a": {}, "b.c": {}}


def test_flatten_lists_are_leaves():
    d = {"a": [1, {"b": 2}], "c": {"d": (1, 2)}}
    assert flatten(d) == {"a": [1, {"b": 2}], "c.d": (1, 2)}


def test_flatten_non_string_keys():
    assert flatten({1: {2: "x"}, None: 0}) == {"1.2": "x", "None": 0}


def test_flatten_does_not_mutate():
    original = copy.deepcopy(NESTED)
    flatten(NESTED)
    assert NESTED == original


def test_flatten_empty():
    assert flatten({}) == {}


# ----------------------------------------------------------------- unflatten

def test_unflatten_basic():
    assert unflatten({"a.b": 1, "a.c": 2, "d": 3}) == {"a": {"b": 1, "c": 2}, "d": 3}


def test_unflatten_custom_sep():
    assert unflatten({"x/y/z": 1}, sep="/") == {"x": {"y": {"z": 1}}}


@pytest.mark.parametrize(
    "flat",
    [
        {"a": 1, "a.b": 2},
        {"a.b": 2, "a": 1},
        {"a.b": 1, "a.b.c": 2},
    ],
)
def test_unflatten_conflicts_raise(flat):
    with pytest.raises(ValueError):
        unflatten(flat)


def test_roundtrip():
    d = {"server": {"host": "x", "ports": [80, 443], "tls": {"on": True}}, "debug": False}
    assert unflatten(flatten(d)) == d


# ---------------------------------------------------------------- deep_merge

def test_deep_merge_basic():
    base = {"a": {"x": 1, "y": 2}, "b": 1}
    override = {"a": {"y": 3, "z": 4}, "c": 5}
    assert deep_merge(base, override) == {"a": {"x": 1, "y": 3, "z": 4}, "b": 1, "c": 5}


def test_deep_merge_type_changes_override_wins():
    assert deep_merge({"a": {"x": 1}}, {"a": 5}) == {"a": 5}
    assert deep_merge({"a": 5}, {"a": {"x": 1}}) == {"a": {"x": 1}}


def test_deep_merge_does_not_mutate_inputs():
    base = {"a": {"x": 1}, "keep": {"k": 1}}
    override = {"a": {"y": 2}, "new": {"n": 1}}
    base_copy, override_copy = copy.deepcopy(base), copy.deepcopy(override)
    deep_merge(base, override)
    assert base == base_copy
    assert override == override_copy


def test_deep_merge_result_is_independent():
    base = {"keep": {"k": 1}}
    override = {"new": {"n": 1}}
    result = deep_merge(base, override)
    result["keep"]["k"] = 999
    result["new"]["n"] = 999
    assert base == {"keep": {"k": 1}}
    assert override == {"new": {"n": 1}}


# ------------------------------------------------------------------ get_path

CFG = {"db": {"primary": {"host": "db1", "port": 5432}, "replicas": ["db2"]}, "zero": 0}


def test_get_path_found():
    assert get_path(CFG, "db.primary.host") == "db1"
    assert get_path(CFG, "db.replicas") == ["db2"]


def test_get_path_falsy_value_is_not_default():
    assert get_path(CFG, "zero", default="missing") == 0


def test_get_path_missing():
    assert get_path(CFG, "db.primary.user") is None
    assert get_path(CFG, "nope.nope", default="d") == "d"


def test_get_path_through_non_dict():
    assert get_path(CFG, "db.primary.host.length", default="d") == "d"
    assert get_path(CFG, "db.replicas.0", default="d") == "d"


def test_get_path_custom_sep():
    assert get_path(CFG, "db/primary/port", sep="/") == 5432

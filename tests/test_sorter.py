"""Tests for envpatch.sorter."""

import pytest
from envpatch.sorter import (
    sort_env_keys,
    group_by_prefix,
    sorted_groups,
    flatten_sorted_groups,
    _get_prefix,
)


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_NAME": "myapp",
        "APP_ENV": "production",
        "PORT": "8080",
        "SECRET_KEY": "abc123",
    }


def test_get_prefix_with_underscore():
    assert _get_prefix("DB_HOST") == "DB"


def test_get_prefix_no_separator():
    assert _get_prefix("PORT") is None


def test_get_prefix_custom_separator():
    assert _get_prefix("db.host", separator=".") == "db"


def test_sort_env_keys_returns_sorted(sample_env):
    result = sort_env_keys(sample_env)
    keys = list(result.keys())
    assert keys == sorted(keys)


def test_sort_env_keys_preserves_values(sample_env):
    result = sort_env_keys(sample_env)
    assert result["DB_HOST"] == "localhost"
    assert result["PORT"] == "8080"


def test_sort_env_keys_no_sort_returns_original_order(sample_env):
    result = sort_env_keys(sample_env, alphabetical=False)
    assert list(result.keys()) == list(sample_env.keys())


def test_group_by_prefix_creates_correct_groups(sample_env):
    groups = group_by_prefix(sample_env)
    assert "DB" in groups
    assert "APP" in groups
    assert "SECRET" in groups


def test_group_by_prefix_ungrouped_keys(sample_env):
    groups = group_by_prefix(sample_env)
    assert "_ungrouped" in groups
    assert "PORT" in groups["_ungrouped"]


def test_group_by_prefix_db_has_both_keys(sample_env):
    groups = group_by_prefix(sample_env)
    assert "DB_HOST" in groups["DB"]
    assert "DB_PORT" in groups["DB"]


def test_sorted_groups_order_is_alphabetical(sample_env):
    groups = sorted_groups(sample_env)
    prefixes = [p for p, _ in groups if p != "_ungrouped"]
    assert prefixes == sorted(prefixes)


def test_sorted_groups_ungrouped_is_last(sample_env):
    groups = sorted_groups(sample_env)
    last_prefix, _ = groups[-1]
    assert last_prefix == "_ungrouped"


def test_sorted_groups_empty_env():
    result = sorted_groups({})
    assert result == []


def test_flatten_sorted_groups_contains_all_keys(sample_env):
    result = flatten_sorted_groups(sample_env)
    assert set(result.keys()) == set(sample_env.keys())


def test_flatten_sorted_groups_values_preserved(sample_env):
    result = flatten_sorted_groups(sample_env)
    for key, value in sample_env.items():
        assert result[key] == value


def test_flatten_sorted_groups_grouped_keys_come_before_ungrouped(sample_env):
    result = flatten_sorted_groups(sample_env)
    keys = list(result.keys())
    port_index = keys.index("PORT")
    db_index = keys.index("DB_HOST")
    assert db_index < port_index

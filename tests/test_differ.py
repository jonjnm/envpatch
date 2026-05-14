"""Tests for envpatch.differ module."""

import pytest
from envpatch.differ import diff_envs, summary, EnvChange


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
TARGET = {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "abc123"}


def test_diff_detects_added_keys():
    changes = diff_envs(BASE, TARGET)
    added = [c for c in changes if c.change_type == "added"]
    assert len(added) == 1
    assert added[0].key == "SECRET"
    assert added[0].new_value == "abc123"


def test_diff_detects_removed_keys():
    changes = diff_envs(BASE, TARGET)
    removed = [c for c in changes if c.change_type == "removed"]
    assert len(removed) == 1
    assert removed[0].key == "DEBUG"
    assert removed[0].old_value == "true"


def test_diff_detects_modified_keys():
    changes = diff_envs(BASE, TARGET)
    modified = [c for c in changes if c.change_type == "modified"]
    assert len(modified) == 1
    assert modified[0].key == "HOST"
    assert modified[0].old_value == "localhost"
    assert modified[0].new_value == "prod.example.com"


def test_diff_unchanged_keys_not_included():
    changes = diff_envs(BASE, TARGET)
    keys = [c.key for c in changes]
    assert "PORT" not in keys


def test_diff_empty_envs():
    assert diff_envs({}, {}) == []


def test_diff_identical_envs():
    assert diff_envs(BASE, BASE) == []


def test_diff_redact_secrets_masks_values():
    changes = diff_envs(BASE, TARGET, redact_secrets=True)
    for change in changes:
        if change.old_value is not None:
            assert change.old_value == "***"
        if change.new_value is not None:
            assert change.new_value == "***"


def test_diff_results_sorted_by_key():
    base = {"Z": "1", "A": "2"}
    target = {"Z": "2", "B": "3"}
    changes = diff_envs(base, target)
    keys = [c.key for c in changes]
    assert keys == sorted(keys)


def test_summary_counts_correctly():
    changes = diff_envs(BASE, TARGET)
    result = summary(changes)
    assert result == "1 added, 1 removed, 1 modified"


def test_summary_empty():
    assert summary([]) == "0 added, 0 removed, 0 modified"


def test_env_change_repr_added():
    c = EnvChange(key="FOO", change_type="added", new_value="bar")
    assert repr(c) == "+ FOO='bar'"


def test_env_change_repr_removed():
    c = EnvChange(key="FOO", change_type="removed", old_value="bar")
    assert repr(c) == "- FOO='bar'"


def test_env_change_repr_modified():
    c = EnvChange(key="FOO", change_type="modified", old_value="old", new_value="new")
    assert repr(c) == "~ FOO: 'old' -> 'new'"

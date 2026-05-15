"""Tests for differ_strategy module."""

import pytest
from envpatch.differ_strategy import DiffMode, diff_with_mode, count_by_type


@pytest.fixture
def base():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "secret123",
        "PORT": "8080",
    }


@pytest.fixture
def target():
    return {
        "APP_NAME": "myapp-v2",
        "DB_PASSWORD": "newpass",
        "DEBUG": "true",
    }


def test_changes_only_mode_returns_changes(base, target):
    changes = diff_with_mode(base, target, DiffMode.CHANGES_ONLY)
    assert len(changes) > 0


def test_changes_only_excludes_unchanged(base, target):
    base["STABLE"] = "same"
    target["STABLE"] = "same"
    changes = diff_with_mode(base, target, DiffMode.CHANGES_ONLY)
    keys = [c.key for c in changes]
    assert "STABLE" not in keys


def test_keys_only_mode_masks_values(base, target):
    changes = diff_with_mode(base, target, DiffMode.KEYS_ONLY)
    for c in changes:
        if c.old_value is not None:
            assert c.old_value == "***"
        if c.new_value is not None:
            assert c.new_value == "***"


def test_keys_only_mode_preserves_keys(base, target):
    changes = diff_with_mode(base, target, DiffMode.KEYS_ONLY)
    keys = {c.key for c in changes}
    assert "APP_NAME" in keys


def test_redacted_mode_hides_secret_values(base, target):
    changes = diff_with_mode(base, target, DiffMode.REDACTED)
    pw_changes = [c for c in changes if c.key == "DB_PASSWORD"]
    assert len(pw_changes) == 1
    assert pw_changes[0].new_value != "newpass"


def test_redacted_mode_keeps_plain_values(base, target):
    changes = diff_with_mode(base, target, DiffMode.REDACTED)
    app_changes = [c for c in changes if c.key == "APP_NAME"]
    assert len(app_changes) == 1
    assert app_changes[0].new_value == "myapp-v2"


def test_full_mode_returns_all_changes(base, target):
    changes_full = diff_with_mode(base, target, DiffMode.FULL)
    changes_default = diff_with_mode(base, target, DiffMode.CHANGES_ONLY)
    assert len(changes_full) == len(changes_default)


def test_count_by_type_added(base, target):
    changes = diff_with_mode(base, target, DiffMode.CHANGES_ONLY)
    counts = count_by_type(changes)
    assert counts.get("added", 0) >= 1


def test_count_by_type_removed(base, target):
    changes = diff_with_mode(base, target, DiffMode.CHANGES_ONLY)
    counts = count_by_type(changes)
    assert counts.get("removed", 0) >= 1


def test_count_by_type_empty():
    counts = count_by_type([])
    assert counts == {}


def test_diff_with_identical_envs_returns_empty():
    env = {"KEY": "val"}
    changes = diff_with_mode(env, env.copy(), DiffMode.CHANGES_ONLY)
    assert changes == []

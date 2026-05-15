import pytest
from envpatch.renamer import rename_keys, list_renames, RenameError


@pytest.fixture
def base_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "API_KEY": "abc123",
        "BASE_URL": "http://example.com",
    }


def test_rename_single_key(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result
    assert "DB_HOST" not in result
    assert result["DATABASE_HOST"] == "localhost"


def test_rename_preserves_other_keys(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert result["DB_PORT"] == "5432"
    assert result["API_KEY"] == "abc123"


def test_rename_multiple_keys(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"})
    assert "DATABASE_HOST" in result
    assert "DATABASE_PORT" in result
    assert "DB_HOST" not in result
    assert "DB_PORT" not in result


def test_rename_nonexistent_key_raises(base_env):
    with pytest.raises(RenameError, match="MISSING"):
        rename_keys(base_env, {"MISSING": "NEW_KEY"})


def test_rename_to_existing_key_raises(base_env):
    with pytest.raises(RenameError, match="DB_PORT"):
        rename_keys(base_env, {"DB_HOST": "DB_PORT"})


def test_rename_swap_is_allowed(base_env):
    # both keys are being renamed away, so swapping should work
    result = rename_keys(base_env, {"DB_HOST": "DB_PORT", "DB_PORT": "DB_HOST"})
    assert result["DB_HOST"] == "5432"
    assert result["DB_PORT"] == "localhost"


def test_update_refs_rewrites_brace_style():
    env = {"OLD_KEY": "value", "OTHER": "see ${OLD_KEY} here"}
    result = rename_keys(env, {"OLD_KEY": "NEW_KEY"}, update_refs=True)
    assert result["OTHER"] == "see ${NEW_KEY} here"


def test_update_refs_rewrites_bare_style():
    env = {"OLD_KEY": "value", "OTHER": "prefix_$OLD_KEY"}
    result = rename_keys(env, {"OLD_KEY": "NEW_KEY"}, update_refs=True)
    assert result["OTHER"] == "prefix_$NEW_KEY"


def test_no_update_refs_leaves_values_unchanged():
    env = {"OLD_KEY": "value", "OTHER": "${OLD_KEY}"}
    result = rename_keys(env, {"OLD_KEY": "NEW_KEY"}, update_refs=False)
    assert result["OTHER"] == "${OLD_KEY}"


def test_list_renames_returns_pairs(base_env):
    pairs = list_renames(base_env, {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"})
    assert ("DB_HOST", "DATABASE_HOST") in pairs
    assert ("DB_PORT", "DATABASE_PORT") in pairs


def test_list_renames_skips_missing_keys(base_env):
    pairs = list_renames(base_env, {"GHOST": "NEW_GHOST"})
    assert pairs == []


def test_rename_empty_env():
    result = rename_keys({}, {})
    assert result == {}

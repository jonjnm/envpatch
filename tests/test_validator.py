import pytest
from envpatch.validator import validate_env, ValidationResult


def test_valid_env_passes():
    env = {"DATABASE_URL": "postgres://localhost/db", "PORT": "5432"}
    result = validate_env(env, required=["DATABASE_URL", "PORT"])
    assert result.is_valid
    assert result.missing_required == []


def test_missing_required_key():
    env = {"PORT": "5432"}
    result = validate_env(env, required=["DATABASE_URL", "PORT"])
    assert not result.is_valid
    assert "DATABASE_URL" in result.missing_required


def test_unknown_key_flagged_when_optional_provided():
    env = {"DATABASE_URL": "x", "MYSTERY_KEY": "y"}
    result = validate_env(env, required=["DATABASE_URL"], optional=["DEBUG"])
    assert "MYSTERY_KEY" in result.unknown_keys
    assert result.is_valid  # unknown keys don't fail validation


def test_no_unknown_keys_when_optional_not_provided():
    env = {"DATABASE_URL": "x", "EXTRA": "y"}
    result = validate_env(env, required=["DATABASE_URL"])
    assert result.unknown_keys == []


def test_type_check_valid_int():
    env = {"PORT": "8080"}
    result = validate_env(env, required=["PORT"], types={"PORT": int})
    assert result.is_valid
    assert result.type_errors == []


def test_type_check_invalid_int():
    env = {"PORT": "not_a_number"}
    result = validate_env(env, required=["PORT"], types={"PORT": int})
    assert not result.is_valid
    assert any("PORT" in e for e in result.type_errors)


def test_type_check_valid_bool():
    for val in ("true", "false", "1", "0", "yes", "no", "True", "FALSE"):
        env = {"DEBUG": val}
        result = validate_env(env, required=["DEBUG"], types={"DEBUG": bool})
        assert result.is_valid, f"Expected {val!r} to be valid bool"


def test_type_check_invalid_bool():
    env = {"DEBUG": "maybe"}
    result = validate_env(env, required=["DEBUG"], types={"DEBUG": bool})
    assert not result.is_valid


def test_type_check_valid_float():
    env = {"RATIO": "0.75"}
    result = validate_env(env, required=["RATIO"], types={"RATIO": float})
    assert result.is_valid


def test_type_check_invalid_float():
    env = {"RATIO": "abc"}
    result = validate_env(env, required=["RATIO"], types={"RATIO": float})
    assert not result.is_valid


def test_summary_all_pass():
    env = {"KEY": "val"}
    result = validate_env(env, required=["KEY"])
    assert result.summary() == "All checks passed."


def test_summary_lists_issues():
    env = {}
    result = validate_env(env, required=["SECRET_KEY"])
    summary = result.summary()
    assert "SECRET_KEY" in summary
    assert "MISSING" in summary


def test_missing_type_key_skipped_gracefully():
    env = {"OTHER": "val"}
    result = validate_env(env, required=[], types={"PORT": int})
    assert result.is_valid

import pytest
from envpatch.interpolator import (
    interpolate_value,
    interpolate_env,
    InterpolationError,
)


# --- interpolate_value ---

def test_brace_style_replaced():
    assert interpolate_value("${HOST}:5432", {"HOST": "localhost"}) == "localhost:5432"


def test_bare_style_replaced():
    assert interpolate_value("$USER@example.com", {"USER": "alice"}) == "alice@example.com"


def test_multiple_references():
    result = interpolate_value(
        "${PROTO}://${HOST}:${PORT}",
        {"PROTO": "https", "HOST": "example.com", "PORT": "443"},
    )
    assert result == "https://example.com:443"


def test_undefined_ref_left_as_is_non_strict():
    result = interpolate_value("${MISSING}", {})
    assert result == "${MISSING}"


def test_undefined_ref_raises_in_strict_mode():
    with pytest.raises(InterpolationError) as exc_info:
        interpolate_value("${MISSING}", {}, strict=True)
    assert "MISSING" in str(exc_info.value)


def test_no_references_returns_unchanged():
    assert interpolate_value("plain_value", {"X": "y"}) == "plain_value"


def test_empty_value():
    assert interpolate_value("", {}) == ""


# --- interpolate_env ---

def test_env_self_referential():
    env = {"HOST": "localhost", "DSN": "postgres://${HOST}/db"}
    result = interpolate_env(env)
    assert result["DSN"] == "postgres://localhost/db"


def test_env_uses_base_for_lookup():
    base = {"HOST": "prod.example.com"}
    env = {"DSN": "postgres://${HOST}/db"}
    result = interpolate_env(env, base=base)
    assert result["DSN"] == "postgres://prod.example.com/db"


def test_env_overrides_base():
    base = {"HOST": "base-host"}
    env = {"HOST": "local-host", "DSN": "${HOST}"}
    result = interpolate_env(env, base=base)
    assert result["DSN"] == "local-host"


def test_env_strict_raises_on_missing():
    env = {"DSN": "${UNDEFINED}"}
    with pytest.raises(InterpolationError) as exc_info:
        interpolate_env(env, strict=True)
    assert "UNDEFINED" in str(exc_info.value)


def test_env_strict_error_includes_key():
    env = {"MY_KEY": "${UNDEFINED}"}
    with pytest.raises(InterpolationError) as exc_info:
        interpolate_env(env, strict=True)
    assert exc_info.value.key == "MY_KEY"


def test_original_env_not_mutated():
    env = {"A": "${B}", "B": "hello"}
    original = dict(env)
    interpolate_env(env)
    assert env == original

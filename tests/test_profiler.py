"""Tests for envpatch.profiler."""

import pytest
from envpatch.profiler import profile_env, ProfileResult, VALUE_LONG_THRESHOLD


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "PORT": "8080",
        "EMPTY_VAR": "",
        "BASE_URL": "https://example.com",
        "LONG_TOKEN": "x" * 80,
        "DEBUG": "true",
    }


def test_total_keys(sample_env):
    result = profile_env(sample_env)
    assert result.total_keys == len(sample_env)


def test_secret_keys_detected(sample_env):
    result = profile_env(sample_env)
    assert "DB_PASSWORD" in result.secret_keys
    assert "API_KEY" in result.secret_keys


def test_plain_keys_not_in_secret(sample_env):
    result = profile_env(sample_env)
    assert "APP_NAME" in result.plain_keys
    assert "PORT" in result.plain_keys


def test_empty_values_detected(sample_env):
    result = profile_env(sample_env)
    assert "EMPTY_VAR" in result.empty_values


def test_no_false_empty_values(sample_env):
    result = profile_env(sample_env)
    assert "APP_NAME" not in result.empty_values


def test_long_values_detected(sample_env):
    result = profile_env(sample_env)
    assert "LONG_TOKEN" in result.long_values


def test_short_values_not_long(sample_env):
    result = profile_env(sample_env)
    assert "APP_NAME" not in result.long_values


def test_numeric_values_detected(sample_env):
    result = profile_env(sample_env)
    assert "PORT" in result.numeric_values


def test_non_numeric_not_flagged(sample_env):
    result = profile_env(sample_env)
    assert "APP_NAME" not in result.numeric_values


def test_url_values_detected(sample_env):
    result = profile_env(sample_env)
    assert "BASE_URL" in result.url_values


def test_non_url_not_flagged(sample_env):
    result = profile_env(sample_env)
    assert "APP_NAME" not in result.url_values


def test_empty_env_returns_zero_totals():
    result = profile_env({})
    assert result.total_keys == 0
    assert result.secret_keys == []
    assert result.plain_keys == []


def test_summary_contains_expected_labels(sample_env):
    result = profile_env(sample_env)
    summary = result.summary()
    assert "Total keys" in summary
    assert "Secret keys" in summary
    assert "Empty values" in summary

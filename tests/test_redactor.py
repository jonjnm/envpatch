"""Tests for envpatch.redactor."""

import pytest
from envpatch.redactor import (
    is_secret_key,
    redact_value,
    redact_env,
    redact_diff_line,
    REDACTED_PLACEHOLDER,
)


# --- is_secret_key ---

def test_password_key_is_secret():
    assert is_secret_key("DB_PASSWORD") is True

def test_token_key_is_secret():
    assert is_secret_key("GITHUB_TOKEN") is True

def test_api_key_is_secret():
    assert is_secret_key("STRIPE_API_KEY") is True

def test_secret_key_is_secret():
    assert is_secret_key("APP_SECRET") is True

def test_private_key_is_secret():
    assert is_secret_key("RSA_PRIVATE_KEY") is True

def test_database_url_is_secret():
    assert is_secret_key("DATABASE_URL") is True

def test_plain_key_not_secret():
    assert is_secret_key("APP_ENV") is False

def test_port_not_secret():
    assert is_secret_key("PORT") is False

def test_debug_not_secret():
    assert is_secret_key("DEBUG") is False


# --- redact_value ---

def test_redact_value_masks_secret():
    assert redact_value("DB_PASSWORD", "supersecret") == REDACTED_PLACEHOLDER

def test_redact_value_keeps_plain():
    assert redact_value("APP_ENV", "production") == "production"

def test_redact_value_custom_placeholder():
    assert redact_value("API_KEY", "abc123", placeholder="[hidden]") == "[hidden]"


# --- redact_env ---

def test_redact_env_masks_secrets():
    env = {"DB_PASSWORD": "s3cr3t", "APP_ENV": "staging", "GITHUB_TOKEN": "tok"}
    result = redact_env(env)
    assert result["DB_PASSWORD"] == REDACTED_PLACEHOLDER
    assert result["GITHUB_TOKEN"] == REDACTED_PLACEHOLDER
    assert result["APP_ENV"] == "staging"

def test_redact_env_does_not_mutate_original():
    env = {"DB_PASSWORD": "s3cr3t"}
    redact_env(env)
    assert env["DB_PASSWORD"] == "s3cr3t"

def test_redact_env_empty():
    assert redact_env({}) == {}


# --- redact_diff_line ---

def test_redact_diff_line_masks_secret():
    assert redact_diff_line("SECRET_KEY", "abc") == REDACTED_PLACEHOLDER

def test_redact_diff_line_keeps_plain():
    assert redact_diff_line("LOG_LEVEL", "info") == "info"

def test_redact_diff_line_none_passthrough():
    assert redact_diff_line("DB_PASSWORD", None) is None

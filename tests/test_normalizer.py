"""Tests for envpatch.normalizer."""

import pytest
from envpatch.normalizer import (
    to_upper_snake,
    normalize_keys,
    list_renames_needed,
    is_normalized,
    NormalizeError,
)


def test_to_upper_snake_already_normalized():
    assert to_upper_snake('DATABASE_URL') == 'DATABASE_URL'


def test_to_upper_snake_lowercased():
    assert to_upper_snake('database_url') == 'DATABASE_URL'


def test_to_upper_snake_hyphens_replaced():
    assert to_upper_snake('db-host') == 'DB_HOST'


def test_to_upper_snake_dots_replaced():
    assert to_upper_snake('app.secret') == 'APP_SECRET'


def test_to_upper_snake_camel_case():
    assert to_upper_snake('apiKey') == 'API_KEY'


def test_to_upper_snake_mixed():
    assert to_upper_snake('myApp-secret.key') == 'MY_APP_SECRET_KEY'


def test_to_upper_snake_collapses_multiple_underscores():
    assert to_upper_snake('foo__bar') == 'FOO_BAR'


def test_normalize_keys_all_already_normalized():
    env = {'HOST': 'localhost', 'PORT': '5432'}
    result = normalize_keys(env)
    assert result == env


def test_normalize_keys_renames_lowercase():
    env = {'host': 'localhost', 'port': '5432'}
    result = normalize_keys(env)
    assert 'HOST' in result
    assert 'PORT' in result
    assert result['HOST'] == 'localhost'


def test_normalize_keys_preserves_values():
    env = {'api-key': 'abc123'}
    result = normalize_keys(env)
    assert result['API_KEY'] == 'abc123'


def test_normalize_keys_collision_raises():
    env = {'api_key': 'one', 'api-key': 'two'}
    with pytest.raises(NormalizeError, match='collision'):
        normalize_keys(env)


def test_normalize_keys_unknown_strategy_raises():
    env = {'KEY': 'val'}
    with pytest.raises(NormalizeError, match='Unknown'):
        normalize_keys(env, strategy='kebab')


def test_list_renames_needed_returns_only_changed():
    env = {'HOST': 'localhost', 'api-key': 'secret', 'db_url': 'postgres://'}
    renames = list_renames_needed(env)
    keys = [r[0] for r in renames]
    assert 'api-key' in keys
    assert 'db_url' in keys
    assert 'HOST' not in keys


def test_list_renames_needed_empty_env():
    assert list_renames_needed({}) == []


def test_is_normalized_true():
    assert is_normalized('DATABASE_URL') is True


def test_is_normalized_false_lowercase():
    assert is_normalized('database_url') is False


def test_is_normalized_false_hyphen():
    assert is_normalized('api-key') is False

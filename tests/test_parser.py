"""Tests for envpatch.parser"""

import pytest
from envpatch.parser import parse_env, serialize_env


SAMPLE_ENV = """
# Database config
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp  # production db

SECRET_KEY="super secret value"
EMPTY_VAR=
SINGLE_QUOTED='hello world'
NO_SPACES=simple
"""


def test_parse_basic_key_value():
    result = parse_env("FOO=bar")
    assert result == {"FOO": "bar"}


def test_parse_ignores_comments():
    result = parse_env("# this is a comment\nFOO=bar")
    assert "#" not in result
    assert result["FOO"] == "bar"


def test_parse_ignores_blank_lines():
    result = parse_env("\n\nFOO=bar\n\n")
    assert result == {"FOO": "bar"}


def test_parse_inline_comment_stripped():
    result = parse_env("DB_NAME=myapp  # production db")
    assert result["DB_NAME"] == "myapp"


def test_parse_double_quoted_value():
    result = parse_env('SECRET_KEY="super secret value"')
    assert result["SECRET_KEY"] == "super secret value"


def test_parse_single_quoted_value():
    result = parse_env("GREETING='hello world'")
    assert result["GREETING"] == "hello world"


def test_parse_empty_value():
    result = parse_env("EMPTY_VAR=")
    assert result["EMPTY_VAR"] == ""


def test_parse_full_sample():
    result = parse_env(SAMPLE_ENV)
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"
    assert result["DB_NAME"] == "myapp"
    assert result["SECRET_KEY"] == "super secret value"
    assert result["EMPTY_VAR"] == ""
    assert result["SINGLE_QUOTED"] == "hello world"
    assert result["NO_SPACES"] == "simple"


def test_serialize_round_trip():
    original = {"FOO": "bar", "BAZ": "qux"}
    serialized = serialize_env(original)
    parsed = parse_env(serialized)
    assert parsed == original


def test_serialize_quotes_values_with_spaces():
    serialized = serialize_env({"MSG": "hello world"})
    assert 'MSG="hello world"' in serialized


def test_serialize_quotes_empty_value():
    serialized = serialize_env({"EMPTY": ""})
    assert 'EMPTY=""' in serialized

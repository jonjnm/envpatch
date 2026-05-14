import pytest
from envpatch.schema import parse_schema


SAMPLE_SCHEMA = """
# Database config
DATABASE_URL | required | type:str
PORT | required | type:int
DEBUG | optional | type:bool
LOG_LEVEL | optional
"""


def test_parse_required_keys():
    schema = parse_schema(SAMPLE_SCHEMA)
    assert "DATABASE_URL" in schema["required"]
    assert "PORT" in schema["required"]


def test_parse_optional_keys():
    schema = parse_schema(SAMPLE_SCHEMA)
    assert "DEBUG" in schema["optional"]
    assert "LOG_LEVEL" in schema["optional"]


def test_parse_types():
    schema = parse_schema(SAMPLE_SCHEMA)
    assert schema["types"]["PORT"] is int
    assert schema["types"]["DEBUG"] is bool
    assert schema["types"]["DATABASE_URL"] is str


def test_no_type_for_untyped_key():
    schema = parse_schema(SAMPLE_SCHEMA)
    assert "LOG_LEVEL" not in schema["types"]


def test_comments_ignored():
    schema = parse_schema(SAMPLE_SCHEMA)
    for key in schema["required"] + schema["optional"]:
        assert not key.startswith("#")


def test_blank_lines_ignored():
    schema = parse_schema("\n\n\nKEY | required\n\n")
    assert schema["required"] == ["KEY"]


def test_default_is_required_when_no_marker():
    schema = parse_schema("MY_KEY")
    assert "MY_KEY" in schema["required"]
    assert "MY_KEY" not in schema["optional"]


def test_empty_schema():
    schema = parse_schema("")
    assert schema["required"] == []
    assert schema["optional"] == []
    assert schema["types"] == {}

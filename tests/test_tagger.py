"""Tests for envpatch.tagger."""

import pytest

from envpatch.tagger import (
    TagError,
    filter_by_tag,
    keys_for_tag,
    list_tags,
    parse_tag_file,
    tag_env,
)


TAG_CONTENT = """
# database keys
DB_HOST=infra,database
DB_PORT=infra,database
DB_PASSWORD=infra,database,secret
# app keys
APP_DEBUG=app
APP_SECRET_KEY=app,secret
"""


def test_parse_tag_file_returns_dict():
    tags = parse_tag_file(TAG_CONTENT)
    assert "DB_HOST" in tags
    assert "APP_DEBUG" in tags


def test_parse_tag_file_correct_tags():
    tags = parse_tag_file(TAG_CONTENT)
    assert tags["DB_HOST"] == ["infra", "database"]
    assert tags["DB_PASSWORD"] == ["infra", "database", "secret"]


def test_parse_tag_file_ignores_comments():
    tags = parse_tag_file(TAG_CONTENT)
    assert len(tags) == 5


def test_parse_tag_file_ignores_blank_lines():
    tags = parse_tag_file("\n\nDB_HOST=infra\n\n")
    assert list(tags.keys()) == ["DB_HOST"]


def test_parse_tag_file_missing_equals_raises():
    with pytest.raises(TagError):
        parse_tag_file("DB_HOST infra")


def test_parse_tag_file_empty_key_raises():
    with pytest.raises(TagError):
        parse_tag_file("=infra,database")


def test_tag_env_includes_all_keys():
    env = {"DB_HOST": "localhost", "UNKNOWN": "val"}
    tags = {"DB_HOST": ["infra"]}
    result = tag_env(env, tags)
    assert set(result.keys()) == {"DB_HOST", "UNKNOWN"}


def test_tag_env_unknown_key_gets_empty_tags():
    env = {"UNKNOWN": "val"}
    result = tag_env(env, {})
    assert result["UNKNOWN"]["tags"] == []


def test_tag_env_value_preserved():
    env = {"DB_HOST": "localhost"}
    tags = {"DB_HOST": ["infra"]}
    result = tag_env(env, tags)
    assert result["DB_HOST"]["value"] == "localhost"


def test_filter_by_tag_returns_matching_keys():
    env = {"DB_HOST": "localhost", "APP_DEBUG": "true", "DB_PORT": "5432"}
    tags = {"DB_HOST": ["infra", "database"], "DB_PORT": ["database"], "APP_DEBUG": ["app"]}
    result = filter_by_tag(env, tags, "database")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_by_tag_no_matches_returns_empty():
    env = {"APP_DEBUG": "true"}
    tags = {"APP_DEBUG": ["app"]}
    result = filter_by_tag(env, tags, "secret")
    assert result == {}


def test_list_tags_returns_sorted_unique():
    tags = parse_tag_file(TAG_CONTENT)
    result = list_tags(tags)
    assert result == sorted(set(result))
    assert "secret" in result
    assert "infra" in result


def test_keys_for_tag_returns_sorted():
    tags = {"DB_HOST": ["infra"], "APP_KEY": ["infra", "app"], "DB_PORT": ["infra"]}
    result = keys_for_tag(tags, "infra")
    assert result == ["APP_KEY", "DB_HOST", "DB_PORT"]


def test_keys_for_tag_unknown_tag_returns_empty():
    tags = {"DB_HOST": ["infra"]}
    assert keys_for_tag(tags, "nope") == []

"""Tests for envpatch.cli_profile."""

import json
import pytest
from unittest.mock import patch, mock_open
from envpatch.cli_profile import build_parser, cmd_profile


ENV_CONTENT = """APP_NAME=myapp
DB_PASSWORD=secret
PORT=9000
EMPTY=
BASE_URL=https://example.com
"""


@pytest.fixture
def tmp_env(tmp_path):
    p = tmp_path / ".env"
    p.write_text(ENV_CONTENT)
    return str(p)


def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser is not None


def test_cmd_profile_exits_zero(tmp_env):
    parser = build_parser()
    args = parser.parse_args([tmp_env])
    assert cmd_profile(args) == 0


def test_cmd_profile_missing_file_exits_one(tmp_path):
    parser = build_parser()
    args = parser.parse_args([str(tmp_path / "missing.env")])
    assert cmd_profile(args) == 1


def test_cmd_profile_json_output(tmp_env, capsys):
    parser = build_parser()
    args = parser.parse_args(["--json", tmp_env])
    result = cmd_profile(args)
    assert result == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "total_keys" in data
    assert "secret_keys" in data
    assert "DB_PASSWORD" in data["secret_keys"]


def test_cmd_profile_summary_output(tmp_env, capsys):
    parser = build_parser()
    args = parser.parse_args([tmp_env])
    cmd_profile(args)
    captured = capsys.readouterr()
    assert "Total keys" in captured.out


def test_cmd_profile_verbose_shows_secret_keys(tmp_env, capsys):
    parser = build_parser()
    args = parser.parse_args(["-v", tmp_env])
    cmd_profile(args)
    captured = capsys.readouterr()
    assert "DB_PASSWORD" in captured.out


def test_cmd_profile_verbose_shows_empty_keys(tmp_env, capsys):
    parser = build_parser()
    args = parser.parse_args(["-v", tmp_env])
    cmd_profile(args)
    captured = capsys.readouterr()
    assert "EMPTY" in captured.out

"""Tests for cli_diff module."""

import pytest
from unittest.mock import patch
from envpatch.cli_diff import build_parser, cmd_diff


@pytest.fixture
def base_env(tmp_path):
    f = tmp_path / "base.env"
    f.write_text("APP=old\nSECRET=abc\nPORT=3000\n")
    return str(f)


@pytest.fixture
def target_env(tmp_path):
    f = tmp_path / "target.env"
    f.write_text("APP=new\nSECRET=xyz\nDEBUG=true\n")
    return str(f)


def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser is not None


def test_parser_default_mode():
    parser = build_parser()
    args = parser.parse_args(["a.env", "b.env"])
    assert args.mode == "changes_only"


def test_parser_accepts_redacted_mode():
    parser = build_parser()
    args = parser.parse_args(["a.env", "b.env", "--mode", "redacted"])
    assert args.mode == "redacted"


def test_parser_summary_flag_default_false():
    parser = build_parser()
    args = parser.parse_args(["a.env", "b.env"])
    assert args.summary is False


def test_cmd_diff_exits_zero(base_env, target_env):
    parser = build_parser()
    args = parser.parse_args([base_env, target_env])
    result = cmd_diff(args)
    assert result == 0


def test_cmd_diff_missing_base_exits_one(tmp_path, target_env):
    parser = build_parser()
    args = parser.parse_args([str(tmp_path / "nope.env"), target_env])
    result = cmd_diff(args)
    assert result == 1


def test_cmd_diff_missing_target_exits_one(base_env, tmp_path):
    parser = build_parser()
    args = parser.parse_args([base_env, str(tmp_path / "nope.env")])
    result = cmd_diff(args)
    assert result == 1


def test_cmd_diff_summary_flag(base_env, target_env, capsys):
    parser = build_parser()
    args = parser.parse_args([base_env, target_env, "--summary"])
    result = cmd_diff(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "total" in captured.out


def test_cmd_diff_identical_envs_prints_no_diff(tmp_path):
    env = tmp_path / "same.env"
    env.write_text("KEY=val\n")
    parser = build_parser()
    args = parser.parse_args([str(env), str(env)])
    result = cmd_diff(args)
    assert result == 0


def test_cmd_diff_redacted_mode_runs(base_env, target_env):
    parser = build_parser()
    args = parser.parse_args([base_env, target_env, "--mode", "redacted"])
    result = cmd_diff(args)
    assert result == 0

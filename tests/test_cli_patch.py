"""Tests for envpatch.cli_patch module."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from envpatch.cli_patch import build_parser, cmd_create, cmd_apply, cmd_show


@pytest.fixture
def base_env(tmp_path):
    f = tmp_path / "base.env"
    f.write_text("HOST=localhost\nPORT=5432\n")
    return f


@pytest.fixture
def target_env(tmp_path):
    f = tmp_path / "target.env"
    f.write_text("HOST=prod.example.com\nPORT=5432\nNEW=1\n")
    return f


def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser is not None


def test_create_command_exits_zero(tmp_path, base_env, target_env):
    patch_out = tmp_path / "out.patch"
    args = MagicMock()
    args.base = str(base_env)
    args.target = str(target_env)
    args.output = str(patch_out)
    args.verbose = False
    args.redact = False
    result = cmd_create(args)
    assert result == 0
    assert patch_out.exists()


def test_create_command_missing_file_exits_one(tmp_path):
    args = MagicMock()
    args.base = str(tmp_path / "nope.env")
    args.target = str(tmp_path / "also_nope.env")
    args.output = str(tmp_path / "out.patch")
    args.verbose = False
    args.redact = False
    result = cmd_create(args)
    assert result == 1


def test_apply_command_exits_zero(tmp_path, base_env, target_env):
    patch_out = tmp_path / "out.patch"
    from envpatch.patcher import create_patch
    create_patch(base_env, target_env, patch_out)

    result_out = tmp_path / "result.env"
    args = MagicMock()
    args.base = str(base_env)
    args.patch = str(patch_out)
    args.output = str(result_out)
    result = cmd_apply(args)
    assert result == 0
    assert result_out.exists()


def test_apply_command_bad_patch_exits_one(tmp_path, base_env):
    bad_patch = tmp_path / "bad.patch"
    bad_patch.write_text("NOT VALID\n")
    args = MagicMock()
    args.base = str(base_env)
    args.patch = str(bad_patch)
    args.output = str(tmp_path / "result.env")
    result = cmd_apply(args)
    assert result == 1


def test_show_command_exits_zero(tmp_path, base_env, target_env):
    patch_out = tmp_path / "out.patch"
    from envpatch.patcher import create_patch
    create_patch(base_env, target_env, patch_out)

    args = MagicMock()
    args.patch = str(patch_out)
    args.redact = False
    result = cmd_show(args)
    assert result == 0


def test_show_command_missing_patch_exits_one(tmp_path):
    args = MagicMock()
    args.patch = str(tmp_path / "nope.patch")
    args.redact = False
    result = cmd_show(args)
    assert result == 1


def test_main_no_command_exits_one():
    from envpatch.cli_patch import main
    with patch("sys.argv", ["envpatch"]):
        result = main()
    assert result == 1

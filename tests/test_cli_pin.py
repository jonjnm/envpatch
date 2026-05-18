"""Tests for envpatch.cli_pin."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from envpatch.cli_pin import build_parser, cmd_lock, cmd_verify


@pytest.fixture
def tmp_env(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PASS=secret\n")
    return str(p)


@pytest.fixture
def tmp_lockfile(tmp_path, tmp_env):
    from envpatch.parser import parse_env
    from envpatch.pinner import create_lockfile, save_lockfile
    env = parse_env(Path(tmp_env).read_text())
    lf = create_lockfile(env)
    p = tmp_path / ".env.lock"
    save_lockfile(lf, str(p))
    return str(p)


def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser is not None


def test_parser_has_lock_subcommand():
    parser = build_parser()
    args = parser.parse_args(["lock", "somefile"])
    assert args.command == "lock"


def test_parser_has_verify_subcommand():
    parser = build_parser()
    args = parser.parse_args(["verify", "somefile", "some.lock"])
    assert args.command == "verify"


def test_lock_default_output():
    parser = build_parser()
    args = parser.parse_args(["lock", "myfile"])
    assert args.output == ".env.lock"


def test_cmd_lock_exits_zero(tmp_path, tmp_env):
    out = str(tmp_path / "out.lock")
    parser = build_parser()
    args = parser.parse_args(["lock", tmp_env, "--output", out])
    assert cmd_lock(args) == 0


def test_cmd_lock_creates_file(tmp_path, tmp_env):
    out = str(tmp_path / "out.lock")
    parser = build_parser()
    args = parser.parse_args(["lock", tmp_env, "--output", out])
    cmd_lock(args)
    assert Path(out).exists()


def test_cmd_lock_missing_file_exits_one(tmp_path):
    out = str(tmp_path / "out.lock")
    parser = build_parser()
    args = parser.parse_args(["lock", "/no/such/file", "--output", out])
    assert cmd_lock(args) == 1


def test_cmd_verify_exits_zero(tmp_env, tmp_lockfile):
    parser = build_parser()
    args = parser.parse_args(["verify", tmp_env, tmp_lockfile])
    assert cmd_verify(args) == 0


def test_cmd_verify_json_flag(tmp_env, tmp_lockfile, capsys):
    parser = build_parser()
    args = parser.parse_args(["verify", tmp_env, tmp_lockfile, "--json"])
    cmd_verify(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert all(v == "ok" for v in data.values())


def test_cmd_verify_mismatch_exits_one(tmp_path, tmp_lockfile):
    modified = tmp_path / "modified.env"
    modified.write_text("DB_HOST=other\nDB_PASS=changed\n")
    parser = build_parser()
    args = parser.parse_args(["verify", str(modified), tmp_lockfile])
    assert cmd_verify(args) == 1

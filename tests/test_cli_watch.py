"""Tests for envpatch.cli_watch module."""

import argparse
import sys
import threading
import time
import pytest

from envpatch.cli_watch import build_parser, cmd_watch, _make_callback
from envpatch.watcher import WatchEvent


# --- build_parser ---

def test_build_parser_returns_parser():
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_parser_default_interval():
    parser = build_parser()
    args = parser.parse_args([".env"])
    assert args.interval == 1.0


def test_parser_custom_interval():
    parser = build_parser()
    args = parser.parse_args([".env", "--interval", "0.5"])
    assert args.interval == 0.5


def test_parser_no_redact_default_false():
    parser = build_parser()
    args = parser.parse_args([".env"])
    assert args.no_redact is False


def test_parser_no_redact_flag():
    parser = build_parser()
    args = parser.parse_args([".env", "--no-redact"])
    assert args.no_redact is True


# --- _make_callback ---

def test_make_callback_prints_changes(capsys):
    callback = _make_callback(redact=False)
    event = WatchEvent(path=".env", changes=["+ NEW_KEY=hello"])
    callback(event)
    captured = capsys.readouterr()
    assert ".env" in captured.out
    assert "Changes detected" in captured.out


def test_make_callback_with_redact_does_not_crash(capsys):
    callback = _make_callback(redact=True)
    event = WatchEvent(path=".env", changes=["+ SECRET_KEY=abc123"])
    callback(event)  # should not raise
    captured = capsys.readouterr()
    assert captured.out  # something was printed


# --- cmd_watch ---

def test_cmd_watch_missing_file_exits_one(tmp_path):
    parser = build_parser()
    args = parser.parse_args([str(tmp_path / "nonexistent.env")])
    # patch watch_file to raise FileNotFoundError
    import envpatch.cli_watch as cw
    original = cw.watch_file

    def raise_fnf(*a, **kw):
        raise FileNotFoundError

    cw.watch_file = raise_fnf
    result = cmd_watch(args)
    cw.watch_file = original
    assert result == 1


def test_cmd_watch_keyboard_interrupt_exits_zero(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=1\n")
    parser = build_parser()
    args = parser.parse_args([str(env_file), "--interval", "0.05"])

    import envpatch.cli_watch as cw
    original = cw.watch_file

    def raise_interrupt(*a, **kw):
        raise KeyboardInterrupt

    cw.watch_file = raise_interrupt
    result = cmd_watch(args)
    cw.watch_file = original
    assert result == 0

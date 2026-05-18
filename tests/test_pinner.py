"""Tests for envpatch.pinner."""

import json
import pytest
from pathlib import Path

from envpatch.pinner import (
    PinError,
    _hash_value,
    create_lockfile,
    load_lockfile,
    save_lockfile,
    verify_env,
)


def test_hash_value_returns_string():
    result = _hash_value("hello")
    assert isinstance(result, str)


def test_hash_value_length_16():
    assert len(_hash_value("anything")) == 16


def test_hash_value_deterministic():
    assert _hash_value("same") == _hash_value("same")


def test_hash_value_different_inputs_differ():
    assert _hash_value("a") != _hash_value("b")


def test_create_lockfile_has_pins_key():
    lf = create_lockfile({"KEY": "val"})
    assert "pins" in lf


def test_create_lockfile_count_matches():
    env = {"A": "1", "B": "2", "C": "3"}
    lf = create_lockfile(env)
    assert lf["count"] == 3


def test_create_lockfile_label_stored():
    lf = create_lockfile({}, label="production")
    assert lf["label"] == "production"


def test_create_lockfile_default_label_empty():
    lf = create_lockfile({})
    assert lf["label"] == ""


def test_create_lockfile_pins_have_hash_and_value():
    lf = create_lockfile({"FOO": "bar"})
    assert "hash" in lf["pins"]["FOO"]
    assert lf["pins"]["FOO"]["value"] == "bar"


def test_save_and_load_lockfile(tmp_path):
    path = str(tmp_path / "test.lock")
    lf = create_lockfile({"X": "1"})
    save_lockfile(lf, path)
    loaded = load_lockfile(path)
    assert loaded["pins"]["X"]["value"] == "1"


def test_load_lockfile_missing_raises():
    with pytest.raises(PinError, match="not found"):
        load_lockfile("/nonexistent/path.lock")


def test_load_lockfile_invalid_json_raises(tmp_path):
    p = tmp_path / "bad.lock"
    p.write_text("not json")
    with pytest.raises(PinError, match="Invalid"):
        load_lockfile(str(p))


def test_verify_all_ok():
    env = {"KEY": "value"}
    lf = create_lockfile(env)
    results = verify_env(env, lf)
    assert results["KEY"] == "ok"


def test_verify_detects_mismatch():
    lf = create_lockfile({"KEY": "original"})
    results = verify_env({"KEY": "changed"}, lf)
    assert results["KEY"] == "mismatch"


def test_verify_detects_missing():
    lf = create_lockfile({"KEY": "val"})
    results = verify_env({}, lf)
    assert results["KEY"] == "missing"


def test_verify_detects_extra():
    lf = create_lockfile({})
    results = verify_env({"NEW": "val"}, lf)
    assert results["NEW"] == "extra"

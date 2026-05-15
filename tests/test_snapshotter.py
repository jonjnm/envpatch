"""Tests for envpatch.snapshotter."""

import json
import pytest
from pathlib import Path

from envpatch.snapshotter import (
    create_snapshot,
    save_snapshot,
    load_snapshots,
    diff_snapshots,
    SnapshotError,
    _hash_env,
)


SAMPLE_ENV = {"APP_ENV": "production", "PORT": "8080", "SECRET_KEY": "abc123"}


def test_create_snapshot_has_required_keys():
    snap = create_snapshot(SAMPLE_ENV)
    assert "timestamp" in snap
    assert "fingerprint" in snap
    assert "keys" in snap
    assert "count" in snap


def test_create_snapshot_count_matches():
    snap = create_snapshot(SAMPLE_ENV)
    assert snap["count"] == len(SAMPLE_ENV)


def test_create_snapshot_keys_are_sorted():
    snap = create_snapshot(SAMPLE_ENV)
    assert snap["keys"] == sorted(SAMPLE_ENV.keys())


def test_create_snapshot_label_stored():
    snap = create_snapshot(SAMPLE_ENV, label="deploy-v2")
    assert snap["label"] == "deploy-v2"


def test_create_snapshot_empty_label_by_default():
    snap = create_snapshot(SAMPLE_ENV)
    assert snap["label"] == ""


def test_hash_env_is_deterministic():
    assert _hash_env(SAMPLE_ENV) == _hash_env(SAMPLE_ENV)


def test_hash_env_changes_with_content():
    other = {**SAMPLE_ENV, "NEW_KEY": "val"}
    assert _hash_env(SAMPLE_ENV) != _hash_env(other)


def test_save_and_load_snapshot(tmp_path):
    log = str(tmp_path / "snaps.jsonl")
    snap = create_snapshot(SAMPLE_ENV, label="test")
    save_snapshot(snap, log)
    records = load_snapshots(log)
    assert len(records) == 1
    assert records[0]["fingerprint"] == snap["fingerprint"]


def test_load_snapshots_empty_when_no_file(tmp_path):
    records = load_snapshots(str(tmp_path / "missing.jsonl"))
    assert records == []


def test_save_snapshot_appends(tmp_path):
    log = str(tmp_path / "snaps.jsonl")
    snap1 = create_snapshot({"A": "1"})
    snap2 = create_snapshot({"A": "1", "B": "2"})
    save_snapshot(snap1, log)
    save_snapshot(snap2, log)
    records = load_snapshots(log)
    assert len(records) == 2


def test_load_snapshots_raises_on_corrupt(tmp_path):
    log = tmp_path / "snaps.jsonl"
    log.write_text("not valid json\n")
    with pytest.raises(SnapshotError):
        load_snapshots(str(log))


def test_diff_snapshots_detects_added():
    a = create_snapshot({"X": "1"})
    b = create_snapshot({"X": "1", "Y": "2"})
    result = diff_snapshots(a, b)
    assert "Y" in result["added"]
    assert result["removed"] == []


def test_diff_snapshots_detects_removed():
    a = create_snapshot({"X": "1", "Y": "2"})
    b = create_snapshot({"X": "1"})
    result = diff_snapshots(a, b)
    assert "Y" in result["removed"]
    assert result["added"] == []


def test_diff_snapshots_same_flag():
    a = create_snapshot(SAMPLE_ENV)
    b = create_snapshot(SAMPLE_ENV)
    result = diff_snapshots(a, b)
    assert result["same"] is True


def test_diff_snapshots_not_same_when_different():
    a = create_snapshot({"A": "1"})
    b = create_snapshot({"B": "2"})
    result = diff_snapshots(a, b)
    assert result["same"] is False

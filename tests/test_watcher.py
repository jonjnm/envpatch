"""Tests for envpatch.watcher module."""

import os
import time
import threading
import pytest

from envpatch.watcher import WatchEvent, watch_file, get_mtime, _read_env_safe


# --- WatchEvent ---

def test_watch_event_has_changes_true():
    event = WatchEvent(path=".env", changes=["x"])
    assert event.has_changes() is True


def test_watch_event_has_changes_false():
    event = WatchEvent(path=".env", changes=[])
    assert event.has_changes() is False


def test_watch_event_str_contains_path():
    event = WatchEvent(path=".env", changes=["a", "b"])
    assert ".env" in str(event)
    assert "2 changes" in str(event)


def test_watch_event_timestamp_set_automatically():
    before = time.time()
    event = WatchEvent(path=".env", changes=[])
    after = time.time()
    assert before <= event.timestamp <= after


# --- _read_env_safe ---

def test_read_env_safe_returns_dict(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\n")
    result = _read_env_safe(str(env_file))
    assert result == {"KEY": "value"}


def test_read_env_safe_missing_file_returns_empty():
    result = _read_env_safe("/nonexistent/path/.env")
    assert result == {}


# --- get_mtime ---

def test_get_mtime_returns_float(tmp_path):
    f = tmp_path / ".env"
    f.write_text("A=1")
    mtime = get_mtime(str(f))
    assert isinstance(mtime, float)


def test_get_mtime_missing_file_returns_none():
    result = get_mtime("/no/such/file.env")
    assert result is None


# --- watch_file ---

def test_watch_file_emits_event_on_change(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=1\n")

    collected = []

    def write_change():
        time.sleep(0.15)
        env_file.write_text("A=1\nB=2\n")

    t = threading.Thread(target=write_change)
    t.start()

    watch_file(
        path=str(env_file),
        callback=collected.append,
        interval=0.05,
        max_events=1,
    )
    t.join()

    assert len(collected) == 1
    assert collected[0].has_changes()


def test_watch_file_stops_after_max_events(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=1\n")

    events = []

    def write_changes():
        for i in range(3):
            time.sleep(0.1)
            env_file.write_text(f"A={i}\n")

    t = threading.Thread(target=write_changes)
    t.start()

    watch_file(
        path=str(env_file),
        callback=events.append,
        interval=0.05,
        max_events=2,
    )
    t.join()

    assert len(events) == 2

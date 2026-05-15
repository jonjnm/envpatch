"""Integration tests: watcher + differ + redactor working together."""

import time
import threading
import pytest

from envpatch.watcher import watch_file, WatchEvent
from envpatch.redactor import is_secret_key


def _write(path, content):
    with open(path, "w") as f:
        f.write(content)


def test_added_key_shows_in_event(tmp_path):
    env = tmp_path / ".env"
    _write(env, "EXISTING=1\n")

    events = []

    def modify():
        time.sleep(0.12)
        _write(env, "EXISTING=1\nNEW_KEY=hello\n")

    t = threading.Thread(target=modify)
    t.start()
    watch_file(str(env), events.append, interval=0.05, max_events=1)
    t.join()

    assert len(events) == 1
    changes = events[0].changes
    keys = [c.key for c in changes]
    assert "NEW_KEY" in keys


def test_removed_key_shows_in_event(tmp_path):
    env = tmp_path / ".env"
    _write(env, "A=1\nB=2\n")

    events = []

    def modify():
        time.sleep(0.12)
        _write(env, "A=1\n")

    t = threading.Thread(target=modify)
    t.start()
    watch_file(str(env), events.append, interval=0.05, max_events=1)
    t.join()

    keys = [c.key for c in events[0].changes]
    assert "B" in keys


def test_secret_key_detected_in_change(tmp_path):
    env = tmp_path / ".env"
    _write(env, "APP=myapp\n")

    events = []

    def modify():
        time.sleep(0.12)
        _write(env, "APP=myapp\nSECRET_KEY=s3cr3t\n")

    t = threading.Thread(target=modify)
    t.start()
    watch_file(str(env), events.append, interval=0.05, max_events=1)
    t.join()

    changed_keys = [c.key for c in events[0].changes]
    assert any(is_secret_key(k) for k in changed_keys)


def test_no_event_when_file_unchanged(tmp_path):
    env = tmp_path / ".env"
    _write(env, "STABLE=yes\n")

    events = []
    stop = threading.Event()

    def run_watcher():
        # run for a short time with no changes
        import envpatch.watcher as wm
        previous = {"STABLE": "yes"}
        for _ in range(5):
            time.sleep(0.05)
            current = wm._read_env_safe(str(env))
            changes = wm.diff_envs(previous, current)
            if changes:
                events.append(changes)

    t = threading.Thread(target=run_watcher)
    t.start()
    t.join(timeout=1.0)

    assert len(events) == 0

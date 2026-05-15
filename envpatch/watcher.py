"""Watch .env files for changes and emit diffs on modification."""

import os
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

from envpatch.parser import parse_env
from envpatch.differ import diff_envs, EnvChange


@dataclass
class WatchEvent:
    path: str
    changes: list
    timestamp: float = field(default_factory=time.time)

    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def __str__(self) -> str:
        return f"WatchEvent({self.path}, {len(self.changes)} changes at {self.timestamp:.0f})"


def _read_env_safe(path: str) -> dict:
    """Read and parse env file, returning empty dict on failure."""
    try:
        with open(path, "r") as f:
            return parse_env(f.read())
    except (OSError, IOError):
        return {}


def watch_file(
    path: str,
    callback: Callable[[WatchEvent], None],
    interval: float = 1.0,
    max_events: Optional[int] = None,
) -> None:
    """Poll a .env file for changes and invoke callback on each diff.

    Args:
        path: Path to the .env file to watch.
        callback: Called with a WatchEvent whenever changes are detected.
        interval: Polling interval in seconds.
        max_events: Stop after this many events (None = run forever).
    """
    previous = _read_env_safe(path)
    events_emitted = 0

    while True:
        time.sleep(interval)
        current = _read_env_safe(path)
        changes = diff_envs(previous, current)

        if changes:
            event = WatchEvent(path=path, changes=changes)
            callback(event)
            events_emitted += 1
            previous = current

            if max_events is not None and events_emitted >= max_events:
                break


def get_mtime(path: str) -> Optional[float]:
    """Return file modification time or None if file doesn't exist."""
    try:
        return os.path.getmtime(path)
    except OSError:
        return None

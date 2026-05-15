"""Snapshot .env files to track state over time."""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class SnapshotError(Exception):
    pass


def _hash_env(env: dict) -> str:
    """Return a short SHA256 fingerprint of the env dict."""
    stable = json.dumps(env, sort_keys=True).encode()
    return hashlib.sha256(stable).hexdigest()[:12]


def create_snapshot(env: dict, label: Optional[str] = None) -> dict:
    """Build a snapshot record from a parsed env dict."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "label": label or "",
        "fingerprint": _hash_env(env),
        "keys": sorted(env.keys()),
        "count": len(env),
    }


def save_snapshot(snapshot: dict, path: str) -> None:
    """Append a snapshot record to a JSONL snapshot log file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(snapshot) + "\n")


def load_snapshots(path: str) -> list:
    """Read all snapshot records from a JSONL file."""
    p = Path(path)
    if not p.exists():
        return []
    records = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise SnapshotError(f"Corrupt snapshot entry: {exc}") from exc
    return records


def diff_snapshots(a: dict, b: dict) -> dict:
    """Compare two snapshot records and return a summary of changes."""
    keys_a = set(a.get("keys", []))
    keys_b = set(b.get("keys", []))
    return {
        "from_fingerprint": a.get("fingerprint"),
        "to_fingerprint": b.get("fingerprint"),
        "added": sorted(keys_b - keys_a),
        "removed": sorted(keys_a - keys_b),
        "unchanged_count": len(keys_a & keys_b),
        "same": a.get("fingerprint") == b.get("fingerprint"),
    }

"""Pin environment variable values to a lockfile for reproducible deployments."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Dict, Optional


class PinError(Exception):
    pass


def _hash_value(value: str) -> str:
    """Return a short SHA-256 digest of a value."""
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def create_lockfile(env: Dict[str, str], label: Optional[str] = None) -> dict:
    """Build a lockfile dict from an env mapping."""
    pins = {key: {"hash": _hash_value(val), "value": val} for key, val in sorted(env.items())}
    return {
        "label": label or "",
        "count": len(pins),
        "pins": pins,
    }


def save_lockfile(lockfile: dict, path: str) -> None:
    """Write lockfile JSON to disk."""
    Path(path).write_text(json.dumps(lockfile, indent=2))


def load_lockfile(path: str) -> dict:
    """Load a lockfile from disk."""
    p = Path(path)
    if not p.exists():
        raise PinError(f"Lockfile not found: {path}")
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        raise PinError(f"Invalid lockfile JSON: {exc}") from exc


def verify_env(env: Dict[str, str], lockfile: dict) -> Dict[str, str]:
    """Compare env against lockfile pins.

    Returns a dict of key -> status: 'ok' | 'mismatch' | 'missing' | 'extra'.
    """
    pins = lockfile.get("pins", {})
    results: Dict[str, str] = {}

    for key, info in pins.items():
        if key not in env:
            results[key] = "missing"
        elif _hash_value(env[key]) != info["hash"]:
            results[key] = "mismatch"
        else:
            results[key] = "ok"

    for key in env:
        if key not in pins:
            results[key] = "extra"

    return results

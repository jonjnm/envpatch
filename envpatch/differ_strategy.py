"""Context-aware diff strategies for comparing .env files."""

from enum import Enum
from typing import Dict, List
from envpatch.differ import EnvChange, diff_envs


class DiffMode(str, Enum):
    FULL = "full"          # all changes including context lines
    CHANGES_ONLY = "changes_only"  # only added/removed/modified
    KEYS_ONLY = "keys_only"        # just key names, no values
    REDACTED = "redacted"          # values hidden for secrets


def diff_with_mode(
    base: Dict[str, str],
    target: Dict[str, str],
    mode: DiffMode = DiffMode.CHANGES_ONLY,
    context_keys: int = 0,
) -> List[EnvChange]:
    """Return diff changes filtered/transformed by the given mode."""
    changes = diff_envs(base, target)

    if mode == DiffMode.CHANGES_ONLY or mode == DiffMode.FULL:
        return changes

    if mode == DiffMode.KEYS_ONLY:
        return [
            EnvChange(c.key, _mask(c.old_value), _mask(c.new_value), c.change_type)
            for c in changes
        ]

    if mode == DiffMode.REDACTED:
        from envpatch.redactor import is_secret_key, redact_value
        return [
            EnvChange(
                c.key,
                redact_value(c.old_value) if c.old_value and is_secret_key(c.key) else c.old_value,
                redact_value(c.new_value) if c.new_value and is_secret_key(c.key) else c.new_value,
                c.change_type,
            )
            for c in changes
        ]

    return changes


def _mask(value):
    """Replace value with a fixed placeholder."""
    if value is None:
        return None
    return "***"


def count_by_type(changes: List[EnvChange]) -> Dict[str, int]:
    """Return a count of changes grouped by change_type."""
    counts: Dict[str, int] = {}
    for change in changes:
        counts[change.change_type] = counts.get(change.change_type, 0) + 1
    return counts

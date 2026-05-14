"""Diff two parsed .env dictionaries and return structured change sets."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class EnvChange:
    key: str
    change_type: str  # 'added', 'removed', 'modified'
    old_value: Optional[str] = None
    new_value: Optional[str] = None

    def __repr__(self) -> str:
        if self.change_type == "added":
            return f"+ {self.key}={self.new_value!r}"
        if self.change_type == "removed":
            return f"- {self.key}={self.old_value!r}"
        return f"~ {self.key}: {self.old_value!r} -> {self.new_value!r}"


def diff_envs(
    base: Dict[str, str],
    target: Dict[str, str],
    redact_secrets: bool = False,
) -> list[EnvChange]:
    """Return a list of EnvChange objects describing differences from base to target.

    Args:
        base: The source environment dict.
        target: The destination environment dict.
        redact_secrets: If True, mask values with '***' in the output.
    """
    changes: list[EnvChange] = []

    all_keys = sorted(set(base) | set(target))

    for key in all_keys:
        in_base = key in base
        in_target = key in target

        if in_base and not in_target:
            changes.append(
                EnvChange(
                    key=key,
                    change_type="removed",
                    old_value="***" if redact_secrets else base[key],
                )
            )
        elif in_target and not in_base:
            changes.append(
                EnvChange(
                    key=key,
                    change_type="added",
                    new_value="***" if redact_secrets else target[key],
                )
            )
        elif base[key] != target[key]:
            changes.append(
                EnvChange(
                    key=key,
                    change_type="modified",
                    old_value="***" if redact_secrets else base[key],
                    new_value="***" if redact_secrets else target[key],
                )
            )

    return changes


def summary(changes: list[EnvChange]) -> str:
    """Return a human-readable summary string for a list of changes."""
    added = sum(1 for c in changes if c.change_type == "added")
    removed = sum(1 for c in changes if c.change_type == "removed")
    modified = sum(1 for c in changes if c.change_type == "modified")
    return f"{added} added, {removed} removed, {modified} modified"

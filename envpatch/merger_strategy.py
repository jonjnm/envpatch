"""Merge strategies for combining .env files with conflict resolution."""

from enum import Enum
from typing import Dict, Optional
from envpatch.differ import EnvChange


class Strategy(Enum):
    OURS = "ours"        # keep base value on conflict
    THEIRS = "theirs"    # take incoming value on conflict
    PROMPT = "prompt"    # raise so caller can decide
    SKIP = "skip"        # leave conflicting keys untouched


class MergeConflict(Exception):
    """Raised when strategy=PROMPT and a conflict is detected."""

    def __init__(self, key: str, base_value: str, incoming_value: str):
        self.key = key
        self.base_value = base_value
        self.incoming_value = incoming_value
        super().__init__(
            f"Conflict on key '{key}': base={base_value!r} incoming={incoming_value!r}"
        )


def merge_with_strategy(
    base: Dict[str, str],
    incoming: Dict[str, str],
    strategy: Strategy = Strategy.THEIRS,
    protected_keys: Optional[list] = None,
) -> Dict[str, str]:
    """Merge *incoming* into *base* using the given strategy.

    Args:
        base: The original environment dict.
        incoming: The environment dict to merge in.
        strategy: How to resolve conflicting keys.
        protected_keys: Keys that should never be overwritten regardless of strategy.

    Returns:
        A new merged dict.
    """
    protected = set(protected_keys or [])
    result = dict(base)

    for key, value in incoming.items():
        if key in protected:
            continue

        if key not in result:
            # new key — always add
            result[key] = value
            continue

        if result[key] == value:
            # no conflict
            continue

        # conflict
        if strategy == Strategy.THEIRS:
            result[key] = value
        elif strategy == Strategy.OURS:
            pass  # keep existing
        elif strategy == Strategy.SKIP:
            pass  # leave as-is, same as OURS but semantically distinct
        elif strategy == Strategy.PROMPT:
            raise MergeConflict(key, result[key], value)

    return result


def list_conflicts(base: Dict[str, str], incoming: Dict[str, str]) -> list:
    """Return a list of keys that conflict between base and incoming."""
    return [
        key
        for key, value in incoming.items()
        if key in base and base[key] != value
    ]

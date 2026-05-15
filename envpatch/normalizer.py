"""Normalize .env key names across environments (casing, separators, etc.)."""

import re
from typing import Dict, List, Tuple


class NormalizeError(Exception):
    pass


def to_upper_snake(key: str) -> str:
    """Convert a key to UPPER_SNAKE_CASE."""
    # Replace hyphens and dots with underscores
    key = re.sub(r'[\-\.]+', '_', key)
    # Insert underscore before uppercase letters that follow lowercase
    key = re.sub(r'([a-z])([A-Z])', r'\1_\2', key)
    # Collapse multiple underscores
    key = re.sub(r'_+', '_', key)
    return key.upper().strip('_')


def normalize_keys(env: Dict[str, str], strategy: str = 'upper_snake') -> Dict[str, str]:
    """Return a new env dict with all keys normalized.

    Raises NormalizeError if two keys collide after normalization.
    """
    if strategy != 'upper_snake':
        raise NormalizeError(f"Unknown normalization strategy: {strategy!r}")

    result: Dict[str, str] = {}
    seen: Dict[str, str] = {}  # normalized -> original

    for original_key, value in env.items():
        normalized = to_upper_snake(original_key)
        if normalized in seen:
            raise NormalizeError(
                f"Key collision after normalization: {original_key!r} and "
                f"{seen[normalized]!r} both become {normalized!r}"
            )
        seen[normalized] = original_key
        result[normalized] = value

    return result


def list_renames_needed(env: Dict[str, str], strategy: str = 'upper_snake') -> List[Tuple[str, str]]:
    """Return list of (original, normalized) pairs where a rename is needed."""
    renames = []
    for key in env:
        normalized = to_upper_snake(key) if strategy == 'upper_snake' else key
        if key != normalized:
            renames.append((key, normalized))
    return renames


def is_normalized(key: str, strategy: str = 'upper_snake') -> bool:
    """Return True if the key is already in normalized form."""
    if strategy == 'upper_snake':
        return key == to_upper_snake(key)
    return True

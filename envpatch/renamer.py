"""Rename keys across an env dict, with optional cascading in values via interpolation refs."""

from typing import Dict, List, Optional, Tuple


class RenameError(Exception):
    pass


RenameMap = Dict[str, str]  # old_key -> new_key


def rename_keys(env: Dict[str, str], rename_map: RenameMap, *, update_refs: bool = False) -> Dict[str, str]:
    """Return a new env dict with keys renamed according to rename_map.

    If update_refs is True, occurrences of ${OLD_KEY} or $OLD_KEY in values
    are rewritten to reference the new key name.

    Raises RenameError if a source key does not exist or a target key already
    exists (and is not itself being renamed away).
    """
    _validate_rename_map(env, rename_map)

    result: Dict[str, str] = {}
    for key, value in env.items():
        new_key = rename_map.get(key, key)
        new_value = _rewrite_refs(value, rename_map) if update_refs else value
        result[new_key] = new_value
    return result


def _validate_rename_map(env: Dict[str, str], rename_map: RenameMap) -> None:
    keys_being_removed = set(rename_map.keys())
    keys_being_added = set(rename_map.values())

    for old_key in rename_map:
        if old_key not in env:
            raise RenameError(f"Key '{old_key}' not found in env")

    for new_key in keys_being_added:
        if new_key in env and new_key not in keys_being_removed:
            raise RenameError(f"Target key '{new_key}' already exists in env")


def _rewrite_refs(value: str, rename_map: RenameMap) -> str:
    """Replace ${OLD} and $OLD references in a value string."""
    result = value
    for old_key, new_key in rename_map.items():
        result = result.replace(f"${{{old_key}}}", f"${{{new_key}}}")
        # bare $KEY only when followed by non-word char or end of string
        import re
        result = re.sub(rf"\${re.escape(old_key)}(?=\W|$)", f"${new_key}", result)
    return result


def list_renames(env: Dict[str, str], rename_map: RenameMap) -> List[Tuple[str, str]]:
    """Return a list of (old_key, new_key) pairs that will actually change."""
    return [(old, new) for old, new in rename_map.items() if old in env and old != new]

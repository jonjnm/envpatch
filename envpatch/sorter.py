"""Sort and group .env file keys by prefix or alphabetically."""

from typing import Dict, List, Tuple, Optional


def _get_prefix(key: str, separator: str = "_") -> Optional[str]:
    """Return the first segment of a key before the separator, or None."""
    parts = key.split(separator, 1)
    if len(parts) > 1:
        return parts[0]
    return None


def sort_env_keys(env: Dict[str, str], alphabetical: bool = True) -> Dict[str, str]:
    """Return a new dict with keys sorted alphabetically."""
    if not alphabetical:
        return dict(env)
    return dict(sorted(env.items()))


def group_by_prefix(
    env: Dict[str, str], separator: str = "_"
) -> Dict[str, Dict[str, str]]:
    """
    Group env keys by their prefix (first segment before separator).
    Keys with no prefix go into the '_ungrouped' bucket.
    """
    groups: Dict[str, Dict[str, str]] = {}
    for key, value in env.items():
        prefix = _get_prefix(key, separator) or "_ungrouped"
        groups.setdefault(prefix, {})[key] = value
    return groups


def sorted_groups(
    env: Dict[str, str], separator: str = "_"
) -> List[Tuple[str, Dict[str, str]]]:
    """
    Return groups sorted by prefix name, each group's keys sorted alphabetically.
    '_ungrouped' is always placed last.
    """
    groups = group_by_prefix(env, separator)
    result = []
    ungrouped = groups.pop("_ungrouped", {})
    for prefix in sorted(groups):
        result.append((prefix, dict(sorted(groups[prefix].items()))))
    if ungrouped:
        result.append(("_ungrouped", dict(sorted(ungrouped.items()))))
    return result


def flatten_sorted_groups(
    env: Dict[str, str], separator: str = "_"
) -> Dict[str, str]:
    """Flatten sorted groups back into a single ordered dict."""
    flat: Dict[str, str] = {}
    for _prefix, group in sorted_groups(env, separator):
        flat.update(group)
    return flat

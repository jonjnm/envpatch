"""Merge .env dicts using a list of EnvChange objects or a direct strategy."""

from typing import Dict, List, Literal
from envpatch.differ import EnvChange, diff_envs


MergeStrategy = Literal["ours", "theirs", "patch"]


def merge_envs(
    base: Dict[str, str],
    target: Dict[str, str],
    strategy: MergeStrategy = "patch",
) -> Dict[str, str]:
    """Merge two env dicts according to the given strategy.

    Strategies:
        - 'ours':   Keep base, ignore target changes entirely.
        - 'theirs': Fully replace with target.
        - 'patch':  Apply only additions and modifications from target;
                    keys removed in target are also removed from result.
    """
    if strategy == "ours":
        return dict(base)
    if strategy == "theirs":
        return dict(target)

    # 'patch' strategy
    return apply_changes(base, diff_envs(base, target))


def apply_changes(
    base: Dict[str, str],
    changes: List[EnvChange],
) -> Dict[str, str]:
    """Apply a list of EnvChange objects onto a base env dict.

    Returns a new dict; the original is not mutated.
    """
    result = dict(base)

    for change in changes:
        if change.change_type == "added":
            if change.new_value is not None:
                result[change.key] = change.new_value
        elif change.change_type == "removed":
            result.pop(change.key, None)
        elif change.change_type == "modified":
            if change.new_value is not None:
                result[change.key] = change.new_value

    return result


def merge_with_defaults(
    base: Dict[str, str],
    defaults: Dict[str, str],
) -> Dict[str, str]:
    """Fill missing keys in base from defaults without overwriting existing values."""
    result = dict(base)
    for key, value in defaults.items():
        if key not in result:
            result[key] = value
    return result

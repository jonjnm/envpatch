"""Formatter module — pretty-prints diffs with optional secret redaction."""

from typing import Iterable
from envpatch.differ import EnvChange
from envpatch.redactor import redact_diff_line

_COLORS = {
    "added": "\033[32m",    # green
    "removed": "\033[31m",  # red
    "modified": "\033[33m", # yellow
    "reset": "\033[0m",
}


def _colorize(text: str, change_type: str, use_color: bool) -> str:
    if not use_color:
        return text
    color = _COLORS.get(change_type, "")
    return f"{color}{text}{_COLORS['reset']}"


def format_changes(
    changes: Iterable[EnvChange],
    *,
    redact: bool = True,
    use_color: bool = False,
) -> list[str]:
    """Return a list of human-readable lines describing each change.

    Args:
        changes: Iterable of EnvChange objects from diff_envs().
        redact:  When True, secret values are masked before display.
        use_color: When True, ANSI color codes are added.
    """
    lines: list[str] = []

    for change in changes:
        old = change.old_value
        new = change.new_value

        if redact:
            old = redact_diff_line(change.key, old)
            new = redact_diff_line(change.key, new)

        if change.change_type == "added":
            line = f"+ {change.key}={new}"
        elif change.change_type == "removed":
            line = f"- {change.key}={old}"
        elif change.change_type == "modified":
            line = f"~ {change.key}: {old} -> {new}"
        else:
            line = f"  {change.key} (unchanged)"

        lines.append(_colorize(line, change.change_type, use_color))

    return lines


def print_changes(
    changes: Iterable[EnvChange],
    *,
    redact: bool = True,
    use_color: bool = True,
) -> None:
    """Print formatted changes to stdout."""
    for line in format_changes(changes, redact=redact, use_color=use_color):
        print(line)

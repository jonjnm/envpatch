"""Utilities for validating and describing the envpatch patch file format."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

PATCH_EXTENSION = ".patch"
PATCH_HEADER = "# envpatch"
_VALID_PREFIXES = ("+", "-", "#")


@dataclass
class PatchFormatError:
    line_number: int
    line: str
    reason: str

    def __str__(self) -> str:
        return f"Line {self.line_number}: {self.reason!r} -> {self.line!r}"


def validate_patch_format(text: str) -> list[PatchFormatError]:
    """Return a list of format errors found in the patch text."""
    errors: list[PatchFormatError] = []
    lines = text.splitlines()

    if not lines or not lines[0].startswith(PATCH_HEADER):
        errors.append(PatchFormatError(1, lines[0] if lines else "", "missing envpatch header"))
        return errors

    for i, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        if not line.startswith(_VALID_PREFIXES):
            errors.append(PatchFormatError(i, line, "line must start with +, -, or #"))
            continue
        if line.startswith("+") and "=" not in line:
            errors.append(PatchFormatError(i, line, "added line missing '=' separator"))

    return errors


def is_patch_file(path: str | Path) -> bool:
    """Return True if the path looks like an envpatch file by extension and header."""
    p = Path(path)
    if p.suffix != PATCH_EXTENSION:
        return False
    try:
        first_line = p.read_text().splitlines()[0]
        return first_line.startswith(PATCH_HEADER)
    except (OSError, IndexError):
        return False


def patch_summary(text: str) -> dict[str, int]:
    """Return a count of added, removed, and comment lines in a patch."""
    counts = {"added": 0, "removed": 0, "comments": 0}
    for line in text.splitlines():
        if line.startswith("+"):
            counts["added"] += 1
        elif line.startswith("-"):
            counts["removed"] += 1
        elif line.startswith("#"):
            counts["comments"] += 1
    return counts

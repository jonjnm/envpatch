"""Apply patch files to .env files, producing a merged result."""

from pathlib import Path
from typing import Optional

from envpatch.parser import parse_env, serialize_env
from envpatch.differ import diff_envs, EnvChange
from envpatch.merger import apply_changes


PATCH_HEADER = "# envpatch"


def write_patch(changes: list[EnvChange], path: str | Path) -> None:
    """Write a list of EnvChange objects to a .patch file."""
    lines = [PATCH_HEADER + "\n"]
    for change in changes:
        if change.change_type == "added":
            lines.append(f"+{change.key}={change.new_value}\n")
        elif change.change_type == "removed":
            lines.append(f"-{change.key}\n")
        elif change.change_type == "modified":
            lines.append(f"-{change.key}\n")
            lines.append(f"+{change.key}={change.new_value}\n")
    Path(path).write_text("".join(lines))


def read_patch(path: str | Path) -> list[EnvChange]:
    """Parse a .patch file back into a list of EnvChange objects."""
    text = Path(path).read_text()
    lines = text.splitlines()
    if not lines or not lines[0].startswith(PATCH_HEADER):
        raise ValueError(f"Not a valid envpatch file: {path}")

    changes: list[EnvChange] = []
    pending_remove: Optional[str] = None

    for line in lines[1:]:
        if not line.strip():
            continue
        if line.startswith("-"):
            pending_remove = line[1:].strip()
        elif line.startswith("+"):
            key, _, value = line[1:].partition("=")
            key = key.strip()
            if pending_remove == key:
                changes.append(EnvChange(key=key, change_type="modified", new_value=value))
                pending_remove = None
            else:
                if pending_remove:
                    changes.append(EnvChange(key=pending_remove, change_type="removed"))
                    pending_remove = None
                changes.append(EnvChange(key=key, change_type="added", new_value=value))

    if pending_remove:
        changes.append(EnvChange(key=pending_remove, change_type="removed"))

    return changes


def create_patch(base_path: str | Path, target_path: str | Path, patch_path: str | Path) -> list[EnvChange]:
    """Diff two env files and write the result as a patch file."""
    base = parse_env(Path(base_path).read_text())
    target = parse_env(Path(target_path).read_text())
    changes = diff_envs(base, target)
    write_patch(changes, patch_path)
    return changes


def apply_patch(base_path: str | Path, patch_path: str | Path, output_path: str | Path) -> dict[str, str]:
    """Apply a patch file to a base .env file and write the result."""
    base = parse_env(Path(base_path).read_text())
    changes = read_patch(patch_path)
    merged = apply_changes(base, changes)
    Path(output_path).write_text(serialize_env(merged))
    return merged

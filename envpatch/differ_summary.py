"""Summarize and categorize diff results for reporting and CLI output."""

from dataclasses import dataclass, field
from typing import List, Dict
from envpatch.differ import EnvChange


@dataclass
class DiffSummary:
    added: List[EnvChange] = field(default_factory=list)
    removed: List[EnvChange] = field(default_factory=list)
    modified: List[EnvChange] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.added) + len(self.removed) + len(self.modified)

    @property
    def is_clean(self) -> bool:
        return self.total == 0

    def summary(self) -> str:
        if self.is_clean:
            return "No differences found."
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        if self.modified:
            parts.append(f"{len(self.modified)} modified")
        return ", ".join(parts) + f" ({self.total} total)"

    def to_dict(self) -> Dict:
        return {
            "added": [c.key for c in self.added],
            "removed": [c.key for c in self.removed],
            "modified": [c.key for c in self.modified],
            "total": self.total,
        }


def build_diff_summary(changes: List[EnvChange]) -> DiffSummary:
    """Partition a flat list of EnvChange objects into a DiffSummary."""
    summary = DiffSummary()
    for change in changes:
        change_type = change.change_type
        if change_type == "added":
            summary.added.append(change)
        elif change_type == "removed":
            summary.removed.append(change)
        elif change_type == "modified":
            summary.modified.append(change)
    return summary


def changes_by_key(changes: List[EnvChange]) -> Dict[str, EnvChange]:
    """Return a dict mapping key -> EnvChange for quick lookup."""
    return {c.key: c for c in changes}

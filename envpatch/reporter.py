"""Generate human-readable reports from env diffs and audit logs."""

from dataclasses import dataclass
from typing import List, Optional
from envpatch.differ import EnvChange
from envpatch.redactor import redact_env
from envpatch.auditor import AuditEntry


@dataclass
class Report:
    title: str
    sections: List[str]

    def __str__(self) -> str:
        divider = "-" * 40
        parts = [f"=== {self.title} ===", divider]
        for section in self.sections:
            parts.append(section)
            parts.append(divider)
        return "\n".join(parts)


def _format_change(change: EnvChange, redact: bool = True) -> str:
    key = change.key
    if change.change_type == "added":
        val = "***" if redact else change.new_value
        return f"  + {key}={val}"
    elif change.change_type == "removed":
        val = "***" if redact else change.old_value
        return f"  - {key}={val}"
    elif change.change_type == "modified":
        old = "***" if redact else change.old_value
        new = "***" if redact else change.new_value
        return f"  ~ {key}: {old} -> {new}"
    return f"  ? {key}"


def build_diff_report(
    changes: List[EnvChange],
    title: str = "Env Diff Report",
    redact: bool = True,
) -> Report:
    if not changes:
        return Report(title=title, sections=["No changes detected."])

    added = [c for c in changes if c.change_type == "added"]
    removed = [c for c in changes if c.change_type == "removed"]
    modified = [c for c in changes if c.change_type == "modified"]

    sections = []
    if added:
        lines = ["Added:"] + [_format_change(c, redact) for c in added]
        sections.append("\n".join(lines))
    if removed:
        lines = ["Removed:"] + [_format_change(c, redact) for c in removed]
        sections.append("\n".join(lines))
    if modified:
        lines = ["Modified:"] + [_format_change(c, redact) for c in modified]
        sections.append("\n".join(lines))

    summary = f"Total: {len(added)} added, {len(removed)} removed, {len(modified)} modified"
    sections.append(summary)
    return Report(title=title, sections=sections)


def build_audit_report(
    entries: List[AuditEntry],
    title: str = "Audit Log Report",
) -> Report:
    if not entries:
        return Report(title=title, sections=["No audit entries found."])

    lines = []
    for entry in entries:
        lines.append(str(entry))

    sections = ["\n".join(lines), f"Total entries: {len(entries)}"]
    return Report(title=title, sections=sections)

"""Audit log for tracking env patch operations."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
import json
import os


@dataclass
class AuditEntry:
    operation: str
    source_file: Optional[str]
    target_file: Optional[str]
    keys_affected: List[str]
    redacted: bool
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "operation": self.operation,
            "source_file": self.source_file,
            "target_file": self.target_file,
            "keys_affected": self.keys_affected,
            "redacted": self.redacted,
        }

    def __str__(self) -> str:
        keys_summary = ", ".join(self.keys_affected[:5])
        if len(self.keys_affected) > 5:
            keys_summary += f" (+{len(self.keys_affected) - 5} more)"
        redacted_note = " [redacted]" if self.redacted else ""
        return (
            f"[{self.timestamp}] {self.operation}{redacted_note} "
            f"keys=[{keys_summary}] "
            f"src={self.source_file} dst={self.target_file}"
        )


def record_entry(log_path: str, entry: AuditEntry) -> None:
    """Append an audit entry to a JSONL log file."""
    os.makedirs(os.path.dirname(log_path) if os.path.dirname(log_path) else ".", exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry.to_dict()) + "\n")


def read_log(log_path: str) -> List[AuditEntry]:
    """Read all audit entries from a JSONL log file."""
    if not os.path.exists(log_path):
        return []
    entries = []
    with open(log_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            entries.append(AuditEntry(
                operation=data["operation"],
                source_file=data["source_file"],
                target_file=data["target_file"],
                keys_affected=data["keys_affected"],
                redacted=data["redacted"],
                timestamp=data["timestamp"],
            ))
    return entries


def summarize_log(entries: List[AuditEntry]) -> str:
    """Return a human-readable summary of audit log entries."""
    if not entries:
        return "No audit entries found."
    lines = [f"Audit log — {len(entries)} entr{'y' if len(entries) == 1 else 'ies'}:"]
    for entry in entries:
        lines.append(f"  {entry}")
    return "\n".join(lines)

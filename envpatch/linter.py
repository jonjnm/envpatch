"""Lint .env files for common issues like duplicate keys, suspicious values, and formatting problems."""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class LintIssue:
    line: int
    key: str
    code: str
    message: str

    def __str__(self):
        return f"Line {self.line} [{self.code}] {self.key}: {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.is_clean:
            return "No issues found."
        lines = [str(issue) for issue in self.issues]
        return "\n".join(lines)


def lint_env(raw_text: str) -> LintResult:
    """Run all lint checks against raw .env file text."""
    result = LintResult()
    seen_keys: Dict[str, int] = {}

    for lineno, raw_line in enumerate(raw_text.splitlines(), start=1):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            result.issues.append(LintIssue(
                line=lineno,
                key="?",
                code="E001",
                message="Line is not a valid key=value pair and is not a comment",
            ))
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        if not key:
            result.issues.append(LintIssue(
                line=lineno, key="", code="E002", message="Empty key name"
            ))
            continue

        if key in seen_keys:
            result.issues.append(LintIssue(
                line=lineno,
                key=key,
                code="W001",
                message=f"Duplicate key (first seen on line {seen_keys[key]})",
            ))
        else:
            seen_keys[key] = lineno

        if " " in key:
            result.issues.append(LintIssue(
                line=lineno, key=key, code="E003", message="Key contains whitespace"
            ))

        if value.startswith(" ") or value.endswith(" "):
            result.issues.append(LintIssue(
                line=lineno, key=key, code="W002", message="Value has leading or trailing whitespace"
            ))

        if value.lower() in ("todo", "fixme", "changeme", "xxx"):
            result.issues.append(LintIssue(
                line=lineno, key=key, code="W003", message=f"Suspicious placeholder value: '{value}'"
            ))

    return result

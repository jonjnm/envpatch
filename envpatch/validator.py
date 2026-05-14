"""Validate .env files against a schema of required and optional keys."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ValidationResult:
    missing_required: list[str] = field(default_factory=list)
    unknown_keys: list[str] = field(default_factory=list)
    type_errors: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not (self.missing_required or self.type_errors)

    def summary(self) -> str:
        lines = []
        for key in self.missing_required:
            lines.append(f"  MISSING (required): {key}")
        for key in self.unknown_keys:
            lines.append(f"  UNKNOWN (not in schema): {key}")
        for msg in self.type_errors:
            lines.append(f"  TYPE ERROR: {msg}")
        if not lines:
            return "All checks passed."
        return "\n".join(lines)


def validate_env(
    env: dict[str, str],
    required: list[str],
    optional: Optional[list[str]] = None,
    types: Optional[dict[str, type]] = None,
) -> ValidationResult:
    """Validate env dict against required keys, optional keys, and type hints."""
    result = ValidationResult()

    for key in required:
        if key not in env:
            result.missing_required.append(key)

    if optional is not None:
        known = set(required) | set(optional)
        for key in env:
            if key not in known:
                result.unknown_keys.append(key)

    if types:
        for key, expected_type in types.items():
            if key not in env:
                continue
            value = env[key]
            if expected_type is int:
                if not value.lstrip("-").isdigit():
                    result.type_errors.append(
                        f"{key}={value!r} is not a valid int"
                    )
            elif expected_type is float:
                try:
                    float(value)
                except ValueError:
                    result.type_errors.append(
                        f"{key}={value!r} is not a valid float"
                    )
            elif expected_type is bool:
                if value.lower() not in ("true", "false", "1", "0", "yes", "no"):
                    result.type_errors.append(
                        f"{key}={value!r} is not a valid bool"
                    )

    return result

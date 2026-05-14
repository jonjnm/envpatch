"""Redactor module — masks secret values before display or logging."""

import re
from typing import Optional

# Keys matching these patterns are considered sensitive
SECRET_PATTERNS = [
    re.compile(r"(password|passwd|pwd)", re.IGNORECASE),
    re.compile(r"(secret|token|api_key|apikey)", re.IGNORECASE),
    re.compile(r"(private_key|privatekey)", re.IGNORECASE),
    re.compile(r"(auth|credential|cred)", re.IGNORECASE),
    re.compile(r"(dsn|database_url|db_url)", re.IGNORECASE),
]

REDACTED_PLACEHOLDER = "***REDACTED***"


def is_secret_key(key: str) -> bool:
    """Return True if the key name looks like it holds a secret value."""
    return any(pattern.search(key) for pattern in SECRET_PATTERNS)


def redact_value(key: str, value: str, placeholder: str = REDACTED_PLACEHOLDER) -> str:
    """Return the value masked if the key is considered sensitive."""
    if is_secret_key(key):
        return placeholder
    return value


def redact_env(
    env: dict[str, str],
    placeholder: str = REDACTED_PLACEHOLDER,
) -> dict[str, str]:
    """Return a copy of *env* with all secret values replaced by *placeholder*."""
    return {
        key: redact_value(key, value, placeholder)
        for key, value in env.items()
    }


def redact_diff_line(
    key: str,
    value: Optional[str],
    placeholder: str = REDACTED_PLACEHOLDER,
) -> Optional[str]:
    """Redact a single value that is part of a diff output.

    Returns None unchanged so callers can distinguish removed keys.
    """
    if value is None:
        return None
    return redact_value(key, value, placeholder)

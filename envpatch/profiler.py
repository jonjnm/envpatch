"""Profile .env files to detect patterns, stats, and anomalies."""

from dataclasses import dataclass, field
from typing import Dict, List
from envpatch.redactor import is_secret_key


@dataclass
class ProfileResult:
    total_keys: int = 0
    secret_keys: List[str] = field(default_factory=list)
    plain_keys: List[str] = field(default_factory=list)
    empty_values: List[str] = field(default_factory=list)
    long_values: List[str] = field(default_factory=list)
    numeric_values: List[str] = field(default_factory=list)
    url_values: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Total keys      : {self.total_keys}",
            f"Secret keys     : {len(self.secret_keys)}",
            f"Plain keys      : {len(self.plain_keys)}",
            f"Empty values    : {len(self.empty_values)}",
            f"Long values     : {len(self.long_values)}",
            f"Numeric values  : {len(self.numeric_values)}",
            f"URL values      : {len(self.url_values)}",
        ]
        return "\n".join(lines)


VALUE_LONG_THRESHOLD = 64
_URL_PREFIXES = ("http://", "https://", "ftp://")


def _is_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def _is_url(value: str) -> bool:
    return any(value.startswith(p) for p in _URL_PREFIXES)


def profile_env(env: Dict[str, str]) -> ProfileResult:
    """Analyse an env dict and return a ProfileResult."""
    result = ProfileResult(total_keys=len(env))

    for key, value in env.items():
        if is_secret_key(key):
            result.secret_keys.append(key)
        else:
            result.plain_keys.append(key)

        if value == "":
            result.empty_values.append(key)
        if len(value) > VALUE_LONG_THRESHOLD:
            result.long_values.append(key)
        if _is_numeric(value):
            result.numeric_values.append(key)
        if _is_url(value):
            result.url_values.append(key)

    return result

"""Variable interpolation for .env files.

Supports ${VAR} and $VAR style references within values.
"""

import re
from typing import Dict, Optional

_BRACE_PATTERN = re.compile(r'\$\{([^}]+)\}')
_BARE_PATTERN = re.compile(r'\$([A-Za-z_][A-Za-z0-9_]*)')


class InterpolationError(Exception):
    def __init__(self, key: str, ref: str):
        self.key = key
        self.ref = ref
        super().__init__(f"Key '{key}' references undefined variable '${ref}'")


def interpolate_value(
    value: str,
    env: Dict[str, str],
    strict: bool = False,
) -> str:
    """Resolve variable references in a single value string."""
    def replace_brace(match: re.Match) -> str:
        ref = match.group(1)
        if ref in env:
            return env[ref]
        if strict:
            raise InterpolationError("<unknown>", ref)
        return match.group(0)

    def replace_bare(match: re.Match) -> str:
        ref = match.group(1)
        if ref in env:
            return env[ref]
        if strict:
            raise InterpolationError("<unknown>", ref)
        return match.group(0)

    result = _BRACE_PATTERN.sub(replace_brace, value)
    result = _BARE_PATTERN.sub(replace_bare, result)
    return result


def interpolate_env(
    env: Dict[str, str],
    base: Optional[Dict[str, str]] = None,
    strict: bool = False,
) -> Dict[str, str]:
    """Interpolate all values in env, optionally using base for lookups.

    Resolution order: env itself first, then base.
    """
    lookup = {}
    if base:
        lookup.update(base)
    lookup.update(env)

    resolved: Dict[str, str] = {}
    for key, value in env.items():
        try:
            resolved[key] = interpolate_value(value, lookup, strict=strict)
        except InterpolationError as exc:
            raise InterpolationError(key, exc.ref) from exc
    return resolved

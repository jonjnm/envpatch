"""Parser for .env files — handles comments, blanks, and quoted values."""

import re
from typing import Dict, List, Tuple

ENV_LINE_RE = re.compile(
    r'^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)$'
)


def parse_env(text: str) -> Dict[str, str]:
    """Parse .env file content into a key/value dict.

    - Strips inline comments (# outside quotes)
    - Handles single and double quoted values
    - Ignores blank lines and comment-only lines
    """
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        match = ENV_LINE_RE.match(line)
        if not match:
            continue
        key = match.group('key')
        value = match.group('value').strip()
        value = _strip_inline_comment(value)
        value = _unquote(value)
        result[key] = value
    return result


def _strip_inline_comment(value: str) -> str:
    """Remove trailing inline comment if value is not quoted."""
    if value and value[0] in ('"', "'"):
        return value  # let _unquote handle quoted strings
    idx = value.find(' #')
    if idx != -1:
        value = value[:idx]
    return value.strip()


def _unquote(value: str) -> str:
    """Strip matching surrounding quotes from a value."""
    if len(value) >= 2:
        if (value[0] == '"' and value[-1] == '"') or \
           (value[0] == "'" and value[-1] == "'"):
            return value[1:-1]
    return value


def serialize_env(data: Dict[str, str]) -> str:
    """Serialize a key/value dict back to .env file content."""
    lines: List[str] = []
    for key, value in data.items():
        if ' ' in value or '#' in value or not value:
            value = f'"{value}"'
        lines.append(f'{key}={value}')
    return '\n'.join(lines) + '\n'

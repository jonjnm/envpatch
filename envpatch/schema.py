"""Load and parse a .env.schema file that declares required/optional keys."""

from pathlib import Path
from typing import Optional


SCHEMA_COMMENT_PREFIX = "#"
REQUIRED_MARKER = "required"
OPTIONAL_MARKER = "optional"
TYPE_MARKER = "type:"


def parse_schema(text: str) -> dict:
    """Parse a schema file and return required, optional, and types."""
    required: list[str] = []
    optional: list[str] = []
    types: dict[str, type] = {}

    type_map = {"int": int, "float": float, "bool": bool, "str": str}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(SCHEMA_COMMENT_PREFIX):
            continue

        parts = [p.strip() for p in line.split("|")]
        key = parts[0]
        if not key:
            continue

        status = REQUIRED_MARKER
        detected_type: Optional[type] = None

        for part in parts[1:]:
            lower = part.lower()
            if lower == OPTIONAL_MARKER:
                status = OPTIONAL_MARKER
            elif lower == REQUIRED_MARKER:
                status = REQUIRED_MARKER
            elif lower.startswith(TYPE_MARKER):
                type_name = lower[len(TYPE_MARKER):].strip()
                detected_type = type_map.get(type_name)

        if status == REQUIRED_MARKER:
            required.append(key)
        else:
            optional.append(key)

        if detected_type is not None:
            types[key] = detected_type

    return {"required": required, "optional": optional, "types": types}


def load_schema(path: str | Path) -> dict:
    """Read a schema file from disk and parse it."""
    return parse_schema(Path(path).read_text(encoding="utf-8"))

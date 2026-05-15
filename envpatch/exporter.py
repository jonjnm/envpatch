"""Export env data to various output formats (JSON, TOML, shell script)."""

import json
from typing import Dict, Optional

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore


SUPPORTED_FORMATS = ("json", "shell", "toml")


class ExportError(Exception):
    pass


def export_as_json(env: Dict[str, str], indent: int = 2) -> str:
    """Serialize env dict to a JSON string."""
    return json.dumps(env, indent=indent, sort_keys=True)


def export_as_shell(env: Dict[str, str], export_keyword: bool = True) -> str:
    """Serialize env dict to a shell-sourceable script."""
    lines = []
    prefix = "export " if export_keyword else ""
    for key in sorted(env):
        value = env[key].replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'{prefix}{key}="{value}"')
    return "\n".join(lines)


def export_as_toml(env: Dict[str, str]) -> str:
    """Serialize env dict to a TOML string (values as strings under [env] table)."""
    lines = ["[env]"]
    for key in sorted(env):
        value = env[key].replace('"', '\\"')
        lines.append(f'{key} = "{value}"')
    return "\n".join(lines)


def export_env(
    env: Dict[str, str],
    fmt: str,
    **kwargs,
) -> str:
    """Export env dict to the requested format string.

    Supported formats: json, shell, toml.
    """
    fmt = fmt.lower()
    if fmt not in SUPPORTED_FORMATS:
        raise ExportError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )
    if fmt == "json":
        return export_as_json(env, **kwargs)
    if fmt == "shell":
        return export_as_shell(env, **kwargs)
    if fmt == "toml":
        return export_as_toml(env)
    raise ExportError(f"Unhandled format: {fmt}")  # pragma: no cover

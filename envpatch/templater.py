"""Template rendering for .env files using a simple {{KEY}} syntax."""

import re
from typing import Dict, Optional


class TemplateError(Exception):
    pass


_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def render_template(template: str, env: Dict[str, str], strict: bool = False) -> str:
    """Replace {{KEY}} placeholders in template with values from env.

    Args:
        template: Template string containing {{KEY}} placeholders.
        env: Mapping of key -> value used for substitution.
        strict: If True, raise TemplateError for missing keys.
                If False, leave unresolved placeholders as-is.

    Returns:
        Rendered string with placeholders replaced.
    """

    def _replace(match: re.Match) -> str:
        key = match.group(1)
        if key in env:
            return env[key]
        if strict:
            raise TemplateError(f"Template key not found in env: {key!r}")
        return match.group(0)

    return _PLACEHOLDER_RE.sub(_replace, template)


def render_template_file(
    template_path: str,
    env: Dict[str, str],
    output_path: Optional[str] = None,
    strict: bool = False,
) -> str:
    """Read a template file, render it, and optionally write the result.

    Returns the rendered content as a string.
    """
    with open(template_path, "r", encoding="utf-8") as fh:
        template = fh.read()

    rendered = render_template(template, env, strict=strict)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(rendered)

    return rendered


def list_placeholders(template: str) -> list:
    """Return a sorted list of unique placeholder keys found in the template."""
    return sorted(set(_PLACEHOLDER_RE.findall(template)))

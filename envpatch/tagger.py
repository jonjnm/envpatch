"""Tag env keys with arbitrary labels for grouping and filtering."""

from typing import Dict, List, Optional


class TagError(Exception):
    pass


def parse_tag_file(content: str) -> Dict[str, List[str]]:
    """Parse a tag definition file.

    Format:
        KEY=tag1,tag2,tag3
        # comments ignored
    Returns dict mapping key -> list of tags.
    """
    tags: Dict[str, List[str]] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise TagError(f"Invalid tag line (missing '='): {line!r}")
        key, _, raw_tags = line.partition("=")
        key = key.strip()
        if not key:
            raise TagError(f"Empty key in tag line: {line!r}")
        tag_list = [t.strip() for t in raw_tags.split(",") if t.strip()]
        tags[key] = tag_list
    return tags


def tag_env(env: Dict[str, str], tags: Dict[str, List[str]]) -> Dict[str, Dict]:
    """Annotate each env key with its tags.

    Returns dict: key -> {"value": ..., "tags": [...]}
    """
    result = {}
    for key, value in env.items():
        result[key] = {"value": value, "tags": tags.get(key, [])}
    return result


def filter_by_tag(env: Dict[str, str], tags: Dict[str, List[str]], tag: str) -> Dict[str, str]:
    """Return subset of env whose keys carry the given tag."""
    return {k: v for k, v in env.items() if tag in tags.get(k, [])}


def list_tags(tags: Dict[str, List[str]]) -> List[str]:
    """Return sorted unique list of all tags defined."""
    seen = set()
    for tag_list in tags.values():
        seen.update(tag_list)
    return sorted(seen)


def keys_for_tag(tags: Dict[str, List[str]], tag: str) -> List[str]:
    """Return sorted list of keys that carry the given tag."""
    return sorted(k for k, tlist in tags.items() if tag in tlist)

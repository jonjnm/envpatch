"""CLI entry point for tagging commands."""

import argparse
import json
import sys
from pathlib import Path

from envpatch.parser import parse_env
from envpatch.tagger import (
    TagError,
    filter_by_tag,
    keys_for_tag,
    list_tags,
    parse_tag_file,
    tag_env,
)


def cmd_annotate(args: argparse.Namespace) -> int:
    """Show env keys annotated with their tags as JSON."""
    try:
        env = parse_env(Path(args.env_file).read_text())
        tags = parse_tag_file(Path(args.tag_file).read_text())
    except (OSError, TagError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    annotated = tag_env(env, tags)
    print(json.dumps(annotated, indent=2, sort_keys=True))
    return 0


def cmd_filter(args: argparse.Namespace) -> int:
    """Print env keys that carry a specific tag."""
    try:
        env = parse_env(Path(args.env_file).read_text())
        tags = parse_tag_file(Path(args.tag_file).read_text())
    except (OSError, TagError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    subset = filter_by_tag(env, tags, args.tag)
    for key, value in sorted(subset.items()):
        print(f"{key}={value}")
    return 0


def cmd_list_tags(args: argparse.Namespace) -> int:
    """List all unique tags defined in a tag file."""
    try:
        tags = parse_tag_file(Path(args.tag_file).read_text())
    except (OSError, TagError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for tag in list_tags(tags):
        keys = keys_for_tag(tags, tag)
        print(f"{tag}: {', '.join(keys)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envpatch-tag", description="Tag env keys")
    sub = parser.add_subparsers(dest="command")

    p_ann = sub.add_parser("annotate", help="Annotate env with tags")
    p_ann.add_argument("env_file")
    p_ann.add_argument("tag_file")
    p_ann.set_defaults(func=cmd_annotate)

    p_flt = sub.add_parser("filter", help="Filter env by tag")
    p_flt.add_argument("env_file")
    p_flt.add_argument("tag_file")
    p_flt.add_argument("tag")
    p_flt.set_defaults(func=cmd_filter)

    p_lst = sub.add_parser("list", help="List all tags")
    p_lst.add_argument("tag_file")
    p_lst.set_defaults(func=cmd_list_tags)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()

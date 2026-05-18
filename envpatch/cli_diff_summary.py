"""CLI entry point for summarizing diffs between two .env files."""

import argparse
import json
import sys

from envpatch.parser import parse_env
from envpatch.differ import diff_envs
from envpatch.differ_summary import build_diff_summary


def cmd_summary(args: argparse.Namespace) -> int:
    try:
        base = parse_env(open(args.base).read())
    except FileNotFoundError:
        print(f"error: file not found: {args.base}", file=sys.stderr)
        return 1

    try:
        target = parse_env(open(args.target).read())
    except FileNotFoundError:
        print(f"error: file not found: {args.target}", file=sys.stderr)
        return 1

    changes = diff_envs(base, target)
    summary = build_diff_summary(changes)

    if args.json:
        print(json.dumps(summary.to_dict(), indent=2))
    else:
        print(summary.summary())
        if not summary.is_clean:
            if summary.added:
                print(f"  + {', '.join(c.key for c in summary.added)}")
            if summary.removed:
                print(f"  - {', '.join(c.key for c in summary.removed)}")
            if summary.modified:
                print(f"  ~ {', '.join(c.key for c in summary.modified)}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envpatch-diff-summary",
        description="Summarize differences between two .env files.",
    )
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("summary", help="Show a summary of changes")
    p.add_argument("base", help="Base .env file")
    p.add_argument("target", help="Target .env file")
    p.add_argument("--json", action="store_true", help="Output as JSON")
    p.set_defaults(func=cmd_summary)

    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()

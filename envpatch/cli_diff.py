"""CLI entry point for diffing two .env files with selectable modes."""

import argparse
import sys
from envpatch.parser import parse_env
from envpatch.differ_strategy import DiffMode, diff_with_mode, count_by_type
from envpatch.formatter import format_changes


def cmd_diff(args):
    try:
        with open(args.base) as f:
            base = parse_env(f.read())
    except FileNotFoundError:
        print(f"error: file not found: {args.base}", file=sys.stderr)
        return 1

    try:
        with open(args.target) as f:
            target = parse_env(f.read())
    except FileNotFoundError:
        print(f"error: file not found: {args.target}", file=sys.stderr)
        return 1

    try:
        mode = DiffMode(args.mode)
    except ValueError:
        print(f"error: unknown mode '{args.mode}'", file=sys.stderr)
        return 1

    changes = diff_with_mode(base, target, mode)

    if not changes:
        print("No differences found.")
        return 0

    if args.summary:
        counts = count_by_type(changes)
        for change_type, count in sorted(counts.items()):
            print(f"  {change_type}: {count}")
        print(f"  total: {len(changes)}")
    else:
        for line in format_changes(changes, colorize=not args.no_color):
            print(line)

    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="envpatch diff",
        description="Diff two .env files.",
    )
    parser.add_argument("base", help="Base .env file")
    parser.add_argument("target", help="Target .env file")
    parser.add_argument(
        "--mode",
        default="changes_only",
        choices=[m.value for m in DiffMode],
        help="Diff mode (default: changes_only)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print counts instead of full diff",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(cmd_diff(args))


if __name__ == "__main__":
    main()

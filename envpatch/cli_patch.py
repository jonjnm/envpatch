"""CLI commands for patch creation and application."""

import argparse
import sys
from pathlib import Path

from envpatch.patcher import create_patch, apply_patch, read_patch
from envpatch.formatter import print_changes


def cmd_create(args: argparse.Namespace) -> int:
    """Create a patch file from two env files."""
    try:
        changes = create_patch(args.base, args.target, args.output)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(f"Patch written to {args.output} ({len(changes)} change(s))")
    if args.verbose:
        print_changes(changes, redact=args.redact)
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    """Apply a patch file to a base env file."""
    try:
        result = apply_patch(args.base, args.patch, args.output)
    except (FileNotFoundError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(f"Applied patch to {args.output} ({len(result)} key(s))")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    """Show the contents of a patch file."""
    try:
        changes = read_patch(args.patch)
    except (FileNotFoundError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print_changes(changes, redact=args.redact)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envpatch",
        description="Diff and merge .env files without leaking secrets.",
    )
    sub = parser.add_subparsers(dest="command")

    p_create = sub.add_parser("create", help="Create a patch from two env files")
    p_create.add_argument("base", help="Base .env file")
    p_create.add_argument("target", help="Target .env file")
    p_create.add_argument("-o", "--output", default="changes.patch", help="Output patch file")
    p_create.add_argument("-v", "--verbose", action="store_true")
    p_create.add_argument("--redact", action="store_true", help="Redact secret values")

    p_apply = sub.add_parser("apply", help="Apply a patch to a base env file")
    p_apply.add_argument("base", help="Base .env file")
    p_apply.add_argument("patch", help="Patch file to apply")
    p_apply.add_argument("-o", "--output", default="result.env", help="Output .env file")

    p_show = sub.add_parser("show", help="Display the contents of a patch file")
    p_show.add_argument("patch", help="Patch file to display")
    p_show.add_argument("--redact", action="store_true", help="Redact secret values")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    dispatch = {"create": cmd_create, "apply": cmd_apply, "show": cmd_show}
    if args.command not in dispatch:
        parser.print_help()
        return 1
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())

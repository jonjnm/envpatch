"""CLI command: envpatch interpolate — resolve variable references in a .env file."""

import argparse
import sys
from pathlib import Path

from .parser import parse_env, serialize_env
from .interpolator import interpolate_env, InterpolationError
from .redactor import redact_env


def cmd_interpolate(args: argparse.Namespace) -> int:
    source = Path(args.file)
    if not source.exists():
        print(f"error: file not found: {source}", file=sys.stderr)
        return 1

    env = parse_env(source.read_text())

    base_env = {}
    if args.base:
        base_path = Path(args.base)
        if not base_path.exists():
            print(f"error: base file not found: {base_path}", file=sys.stderr)
            return 1
        base_env = parse_env(base_path.read_text())

    try:
        resolved = interpolate_env(env, base=base_env or None, strict=args.strict)
    except InterpolationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.redact:
        resolved = redact_env(resolved)

    if args.output:
        Path(args.output).write_text(serialize_env(resolved))
        print(f"Written to {args.output}")
    else:
        print(serialize_env(resolved), end="")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envpatch interpolate",
        description="Resolve $VAR and ${VAR} references in a .env file.",
    )
    parser.add_argument("file", help=".env file to interpolate")
    parser.add_argument(
        "--base", metavar="FILE",
        help="optional base .env file supplying extra variable values",
    )
    parser.add_argument(
        "--output", "-o", metavar="FILE",
        help="write result to FILE instead of stdout",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="exit with error if any reference is unresolved",
    )
    parser.add_argument(
        "--redact", action="store_true",
        help="redact secret values before printing",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(cmd_interpolate(args))


if __name__ == "__main__":
    main()

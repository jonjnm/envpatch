"""CLI entry point for the export subcommand."""

import argparse
import sys
from pathlib import Path

from envpatch.parser import parse_env
from envpatch.exporter import export_env, ExportError, SUPPORTED_FORMATS
from envpatch.redactor import redact_env


def cmd_export(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"error: file not found: {env_path}", file=sys.stderr)
        return 1

    try:
        env = parse_env(env_path.read_text())
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not parse env file: {exc}", file=sys.stderr)
        return 1

    if args.redact:
        env = redact_env(env)

    try:
        output = export_env(env, args.format)
    except ExportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(output + "\n")
        print(f"exported to {out_path}")
    else:
        print(output)

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envpatch export",
        description="Export a .env file to another format.",
    )
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "-f",
        "--format",
        choices=SUPPORTED_FORMATS,
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        default=None,
        help="Write output to FILE instead of stdout",
    )
    parser.add_argument(
        "--redact",
        action="store_true",
        help="Redact secret values before exporting",
    )
    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    sys.exit(cmd_export(args))


if __name__ == "__main__":  # pragma: no cover
    main()

"""CLI entry point for generating reports from diffs and audit logs."""

import argparse
import sys
from envpatch.parser import parse_env
from envpatch.differ import diff_envs
from envpatch.auditor import read_log
from envpatch.reporter import build_diff_report, build_audit_report


def cmd_diff_report(args: argparse.Namespace) -> int:
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
    redact = not args.no_redact
    report = build_diff_report(changes, title="Env Diff Report", redact=redact)
    print(report)
    return 0


def cmd_audit_report(args: argparse.Namespace) -> int:
    try:
        entries = read_log(args.log)
    except FileNotFoundError:
        print(f"error: log file not found: {args.log}", file=sys.stderr)
        return 1

    report = build_audit_report(entries, title="Audit Log Report")
    print(report)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envpatch-report",
        description="Generate reports from env diffs and audit logs.",
    )
    subparsers = parser.add_subparsers(dest="command")

    diff_p = subparsers.add_parser("diff", help="Report on differences between two env files.")
    diff_p.add_argument("base", help="Base .env file")
    diff_p.add_argument("target", help="Target .env file")
    diff_p.add_argument(
        "--no-redact",
        action="store_true",
        default=False,
        help="Show actual values instead of redacting secrets.",
    )

    audit_p = subparsers.add_parser("audit", help="Report on audit log entries.")
    audit_p.add_argument("log", help="Path to audit log file")

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "diff":
        return cmd_diff_report(args)
    elif args.command == "audit":
        return cmd_audit_report(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""CLI commands for pinning and verifying env lockfiles."""

from __future__ import annotations

import argparse
import json
import sys

from envpatch.parser import parse_env
from envpatch.pinner import PinError, create_lockfile, load_lockfile, save_lockfile, verify_env


def cmd_lock(args: argparse.Namespace) -> int:
    try:
        env = parse_env(open(args.env_file).read())
    except FileNotFoundError:
        print(f"error: file not found: {args.env_file}", file=sys.stderr)
        return 1

    lockfile = create_lockfile(env, label=args.label or "")
    save_lockfile(lockfile, args.output)
    print(f"Locked {lockfile['count']} keys to {args.output}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    try:
        env = parse_env(open(args.env_file).read())
        lockfile = load_lockfile(args.lockfile)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except PinError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    results = verify_env(env, lockfile)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for key, status in sorted(results.items()):
            symbol = {"ok": "✓", "mismatch": "✗", "missing": "?", "extra": "+"}.get(status, status)
            print(f"  {symbol}  {key}: {status}")

    bad = [s for s in results.values() if s != "ok"]
    if bad:
        print(f"\n{len(bad)} issue(s) found.", file=sys.stderr)
        return 1
    print("\nAll keys verified OK.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envpatch-pin", description="Pin and verify .env lockfiles")
    sub = parser.add_subparsers(dest="command")

    p_lock = sub.add_parser("lock", help="Create a lockfile from an env file")
    p_lock.add_argument("env_file")
    p_lock.add_argument("--output", default=".env.lock", help="Output lockfile path")
    p_lock.add_argument("--label", default="", help="Optional label for this lockfile")
    p_lock.set_defaults(func=cmd_lock)

    p_verify = sub.add_parser("verify", help="Verify an env file against a lockfile")
    p_verify.add_argument("env_file")
    p_verify.add_argument("lockfile")
    p_verify.add_argument("--json", action="store_true", help="Output results as JSON")
    p_verify.set_defaults(func=cmd_verify)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()

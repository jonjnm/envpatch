"""CLI commands for env snapshots."""

import argparse
import json
import sys

from envpatch.parser import parse_env
from envpatch.snapshotter import (
    create_snapshot,
    save_snapshot,
    load_snapshots,
    diff_snapshots,
    SnapshotError,
)


def cmd_snap(args: argparse.Namespace) -> int:
    try:
        with open(args.env_file, "r", encoding="utf-8") as f:
            env = parse_env(f.read())
    except FileNotFoundError:
        print(f"error: file not found: {args.env_file}", file=sys.stderr)
        return 1

    snapshot = create_snapshot(env, label=args.label)
    save_snapshot(snapshot, args.log)
    print(f"snapshot saved: {snapshot['fingerprint']} ({snapshot['count']} keys)")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    try:
        records = load_snapshots(args.log)
    except SnapshotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not records:
        print("no snapshots found")
        return 0

    for r in records:
        label = f" [{r['label']}]" if r.get("label") else ""
        print(f"{r['timestamp']}  {r['fingerprint']}  {r['count']} keys{label}")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    try:
        records = load_snapshots(args.log)
    except SnapshotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if len(records) < 2:
        print("need at least 2 snapshots to diff", file=sys.stderr)
        return 1

    a, b = records[-2], records[-1]
    result = diff_snapshots(a, b)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["same"]:
            print("snapshots are identical")
        else:
            for k in result["added"]:
                print(f"+ {k}")
            for k in result["removed"]:
                print(f"- {k}")
            print(f"  {result['unchanged_count']} key(s) unchanged")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envpatch-snapshot", description="Snapshot env files")
    parser.add_argument("--log", default=".envpatch_snapshots.jsonl", help="snapshot log file")
    sub = parser.add_subparsers(dest="command")

    p_snap = sub.add_parser("snap", help="take a snapshot")
    p_snap.add_argument("env_file")
    p_snap.add_argument("--label", default="")
    p_snap.set_defaults(func=cmd_snap)

    p_list = sub.add_parser("list", help="list snapshots")
    p_list.set_defaults(func=cmd_list)

    p_diff = sub.add_parser("diff", help="diff last two snapshots")
    p_diff.add_argument("--json", action="store_true")
    p_diff.set_defaults(func=cmd_diff)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    sys.exit(args.func(args))

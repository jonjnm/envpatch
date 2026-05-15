"""CLI entry point for the envpatch watch command."""

import argparse
import sys
from datetime import datetime

from envpatch.watcher import watch_file, WatchEvent
from envpatch.formatter import format_changes
from envpatch.redactor import redact_diff_line


def _make_callback(redact: bool) -> callable:
    def callback(event: WatchEvent) -> None:
        ts = datetime.fromtimestamp(event.timestamp).strftime("%H:%M:%S")
        print(f"\n[{ts}] Changes detected in {event.path}:")
        for change in event.changes:
            line = str(change)
            if redact:
                line = redact_diff_line(line)
            print(f"  {line}")
        print()

    return callback


def cmd_watch(args: argparse.Namespace) -> int:
    path = args.file
    redact = not args.no_redact

    print(f"Watching {path} (interval={args.interval}s, redact={redact})")
    print("Press Ctrl+C to stop.\n")

    try:
        watch_file(
            path=path,
            callback=_make_callback(redact),
            interval=args.interval,
        )
    except KeyboardInterrupt:
        print("\nStopped watching.")
        return 0
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envpatch watch",
        description="Watch a .env file and print diffs on change.",
    )
    parser.add_argument("file", help="Path to the .env file to watch")
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Polling interval in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--no-redact",
        action="store_true",
        default=False,
        help="Disable automatic redaction of secret values",
    )
    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    sys.exit(cmd_watch(args))


if __name__ == "__main__":
    main()

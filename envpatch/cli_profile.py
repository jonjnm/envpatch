"""CLI entry point for the profile command."""

import argparse
import sys
from envpatch.parser import parse_env
from envpatch.profiler import profile_env


def cmd_profile(args: argparse.Namespace) -> int:
    try:
        with open(args.env_file) as fh:
            env = parse_env(fh.read())
    except FileNotFoundError:
        print(f"error: file not found: {args.env_file}", file=sys.stderr)
        return 1

    result = profile_env(env)

    if args.json:
        import json
        data = {
            "total_keys": result.total_keys,
            "secret_keys": result.secret_keys,
            "plain_keys": result.plain_keys,
            "empty_values": result.empty_values,
            "long_values": result.long_values,
            "numeric_values": result.numeric_values,
            "url_values": result.url_values,
        }
        print(json.dumps(data, indent=2))
    else:
        print(result.summary())

        if args.verbose:
            if result.secret_keys:
                print("\nSecret keys:")
                for k in result.secret_keys:
                    print(f"  {k}")
            if result.empty_values:
                print("\nEmpty values:")
                for k in result.empty_values:
                    print(f"  {k}")
            if result.url_values:
                print("\nURL values:")
                for k in result.url_values:
                    print(f"  {k}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envpatch-profile",
        description="Profile a .env file for stats and anomalies.",
    )
    parser.add_argument("env_file", help="Path to .env file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show key lists")
    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    sys.exit(cmd_profile(args))


if __name__ == "__main__":
    main()

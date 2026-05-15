"""CLI entry point for the normalize command."""

import argparse
import sys

from envpatch.parser import parse_env, serialize_env
from envpatch.normalizer import normalize_keys, list_renames_needed, NormalizeError


def cmd_normalize(args: argparse.Namespace) -> int:
    try:
        with open(args.env_file, 'r') as f:
            env = parse_env(f.read())
    except FileNotFoundError:
        print(f"error: file not found: {args.env_file}", file=sys.stderr)
        return 1

    renames = list_renames_needed(env, strategy=args.strategy)

    if args.dry_run:
        if not renames:
            print("All keys are already normalized.")
        else:
            print(f"{len(renames)} key(s) would be renamed:")
            for original, normalized in renames:
                print(f"  {original} -> {normalized}")
        return 0

    try:
        normalized_env = normalize_keys(env, strategy=args.strategy)
    except NormalizeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    output = serialize_env(normalized_env)
    out_path = args.output or args.env_file

    with open(out_path, 'w') as f:
        f.write(output)

    print(f"Normalized {len(renames)} key(s) -> wrote {out_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='envpatch normalize',
        description='Normalize key names in a .env file'
    )
    parser.add_argument('env_file', help='Path to the .env file')
    parser.add_argument(
        '--strategy', default='upper_snake',
        choices=['upper_snake'],
        help='Normalization strategy (default: upper_snake)'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Show what would change without writing'
    )
    parser.add_argument(
        '--output', default=None,
        help='Write result to this path instead of overwriting input'
    )
    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    sys.exit(cmd_normalize(args))


if __name__ == '__main__':
    main()

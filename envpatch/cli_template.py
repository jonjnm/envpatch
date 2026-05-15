"""CLI entry point for the template rendering command."""

import argparse
import sys

from envpatch.parser import parse_env
from envpatch.templater import TemplateError, list_placeholders, render_template_file


def cmd_render(args: argparse.Namespace) -> int:
    try:
        env = parse_env(open(args.env_file).read())
    except FileNotFoundError:
        print(f"error: env file not found: {args.env_file}", file=sys.stderr)
        return 1

    try:
        rendered = render_template_file(
            args.template,
            env,
            output_path=args.output,
            strict=args.strict,
        )
    except FileNotFoundError:
        print(f"error: template file not found: {args.template}", file=sys.stderr)
        return 1
    except TemplateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not args.output:
        print(rendered, end="")

    return 0


def cmd_list(args: argparse.Namespace) -> int:
    try:
        with open(args.template) as fh:
            template = fh.read()
    except FileNotFoundError:
        print(f"error: template file not found: {args.template}", file=sys.stderr)
        return 1

    keys = list_placeholders(template)
    if keys:
        for key in keys:
            print(key)
    else:
        print("(no placeholders found)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envpatch-template", description="Render .env templates")
    sub = parser.add_subparsers(dest="command", required=True)

    p_render = sub.add_parser("render", help="Render a template using an env file")
    p_render.add_argument("template", help="Path to template file")
    p_render.add_argument("env_file", help="Path to .env file")
    p_render.add_argument("-o", "--output", help="Write rendered output to this file")
    p_render.add_argument("--strict", action="store_true", help="Error on missing keys")
    p_render.set_defaults(func=cmd_render)

    p_list = sub.add_parser("list", help="List placeholders in a template")
    p_list.add_argument("template", help="Path to template file")
    p_list.set_defaults(func=cmd_list)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()

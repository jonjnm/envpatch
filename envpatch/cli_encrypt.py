"""CLI commands for encrypting and decrypting .env files."""

import argparse
import sys

from envpatch.encryptor import encrypt_env, decrypt_env, EncryptionError
from envpatch.parser import parse_env, serialize_env
from envpatch.redactor import is_secret_key


def _read_passphrase(args) -> str:
    if args.passphrase:
        return args.passphrase
    import getpass
    return getpass.getpass("Passphrase: ")


def cmd_encrypt(args) -> int:
    try:
        env = parse_env(open(args.input).read())
    except FileNotFoundError:
        print(f"error: file not found: {args.input}", file=sys.stderr)
        return 1

    passphrase = _read_passphrase(args)
    keys = args.keys.split(",") if args.keys else [k for k in env if is_secret_key(k)]

    try:
        encrypted = encrypt_env(env, passphrase, keys)
    except EncryptionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    output = args.output or args.input
    with open(output, "w") as fh:
        fh.write(serialize_env(encrypted))
    print(f"Encrypted {len(keys)} key(s) -> {output}")
    return 0


def cmd_decrypt(args) -> int:
    try:
        env = parse_env(open(args.input).read())
    except FileNotFoundError:
        print(f"error: file not found: {args.input}", file=sys.stderr)
        return 1

    passphrase = _read_passphrase(args)
    keys = args.keys.split(",") if args.keys else None

    try:
        decrypted = decrypt_env(env, passphrase, keys)
    except EncryptionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    output = args.output or args.input
    with open(output, "w") as fh:
        fh.write(serialize_env(decrypted))
    print(f"Decrypted -> {output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envpatch-encrypt", description="Encrypt/decrypt .env secrets")
    sub = parser.add_subparsers(dest="command")

    enc = sub.add_parser("encrypt", help="Encrypt secret keys in an env file")
    enc.add_argument("input", help="Input .env file")
    enc.add_argument("-o", "--output", help="Output file (default: overwrite input)")
    enc.add_argument("-p", "--passphrase", help="Encryption passphrase")
    enc.add_argument("--keys", help="Comma-separated keys to encrypt (default: auto-detect secrets)")
    enc.set_defaults(func=cmd_encrypt)

    dec = sub.add_parser("decrypt", help="Decrypt secret keys in an env file")
    dec.add_argument("input", help="Input .env file")
    dec.add_argument("-o", "--output", help="Output file (default: overwrite input)")
    dec.add_argument("-p", "--passphrase", help="Decryption passphrase")
    dec.add_argument("--keys", help="Comma-separated keys to decrypt (default: all)")
    dec.set_defaults(func=cmd_decrypt)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()

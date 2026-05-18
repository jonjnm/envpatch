"""Entry-point shim for envpatch-pin so it can be registered in pyproject.toml."""

from envpatch.cli_pin import main

if __name__ == "__main__":
    main()

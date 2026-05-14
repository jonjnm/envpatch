"""envpatch — diff and merge .env files across environments without leaking secrets."""

__version__ = "0.1.0"
__author__ = "envpatch contributors"

from envpatch.parser import parse_env, serialize_env

__all__ = ["parse_env", "serialize_env"]

"""Simple symmetric encryption helpers for protecting secret values at rest."""

import base64
import hashlib
import os

try:
    from cryptography.fernet import Fernet, InvalidToken
    _CRYPTO_AVAILABLE = True
except ImportError:
    _CRYPTO_AVAILABLE = False


class EncryptionError(Exception):
    pass


def _require_crypto():
    if not _CRYPTO_AVAILABLE:
        raise EncryptionError(
            "cryptography package is required: pip install cryptography"
        )


def derive_key(passphrase: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    """Derive a Fernet-compatible key from a passphrase. Returns (key, salt)."""
    _require_crypto()
    if salt is None:
        salt = os.urandom(16)
    raw = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, iterations=200_000)
    key = base64.urlsafe_b64encode(raw)
    return key, salt


def encrypt_value(value: str, passphrase: str) -> str:
    """Encrypt a single string value. Returns a compact token string."""
    _require_crypto()
    key, salt = derive_key(passphrase)
    f = Fernet(key)
    token = f.encrypt(value.encode())
    combined = salt + token
    return base64.urlsafe_b64encode(combined).decode()


def decrypt_value(token_str: str, passphrase: str) -> str:
    """Decrypt a value previously encrypted with encrypt_value."""
    _require_crypto()
    try:
        combined = base64.urlsafe_b64decode(token_str.encode())
        salt, token = combined[:16], combined[16:]
        key, _ = derive_key(passphrase, salt)
        f = Fernet(key)
        return f.decrypt(token).decode()
    except (InvalidToken, Exception) as exc:
        raise EncryptionError(f"Decryption failed: {exc}") from exc


def encrypt_env(env: dict[str, str], passphrase: str, keys: list[str] | None = None) -> dict[str, str]:
    """Return a copy of env with specified keys (or all) encrypted."""
    result = dict(env)
    targets = keys if keys is not None else list(env.keys())
    for k in targets:
        if k in result:
            result[k] = encrypt_value(result[k], passphrase)
    return result


def decrypt_env(env: dict[str, str], passphrase: str, keys: list[str] | None = None) -> dict[str, str]:
    """Return a copy of env with specified keys (or all) decrypted."""
    result = dict(env)
    targets = keys if keys is not None else list(env.keys())
    for k in targets:
        if k in result:
            result[k] = decrypt_value(result[k], passphrase)
    return result

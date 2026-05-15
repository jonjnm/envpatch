"""Tests for envpatch.encryptor module."""

import pytest

try:
    from envpatch.encryptor import (
        derive_key,
        encrypt_value,
        decrypt_value,
        encrypt_env,
        decrypt_env,
        EncryptionError,
    )
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

pytest.importorskip("cryptography", reason="cryptography package not installed")

PASS = "hunter2"


def test_derive_key_returns_bytes():
    key, salt = derive_key(PASS)
    assert isinstance(key, bytes)
    assert isinstance(salt, bytes)
    assert len(salt) == 16


def test_derive_key_deterministic_with_salt():
    _, salt = derive_key(PASS)
    key1, _ = derive_key(PASS, salt)
    key2, _ = derive_key(PASS, salt)
    assert key1 == key2


def test_derive_key_different_salt_different_key():
    key1, _ = derive_key(PASS)
    key2, _ = derive_key(PASS)
    assert key1 != key2


def test_encrypt_returns_string():
    token = encrypt_value("mysecret", PASS)
    assert isinstance(token, str)
    assert "mysecret" not in token


def test_decrypt_roundtrip():
    original = "super_secret_value_123"
    token = encrypt_value(original, PASS)
    recovered = decrypt_value(token, PASS)
    assert recovered == original


def test_decrypt_wrong_passphrase_raises():
    token = encrypt_value("value", PASS)
    with pytest.raises(EncryptionError):
        decrypt_value(token, "wrongpass")


def test_decrypt_garbage_raises():
    with pytest.raises(EncryptionError):
        decrypt_value("notavalidtoken", PASS)


def test_encrypt_env_encrypts_specified_keys():
    env = {"DB_PASSWORD": "secret", "APP_NAME": "myapp"}
    result = encrypt_env(env, PASS, keys=["DB_PASSWORD"])
    assert result["APP_NAME"] == "myapp"
    assert result["DB_PASSWORD"] != "secret"


def test_encrypt_env_all_keys_when_none_specified():
    env = {"KEY1": "val1", "KEY2": "val2"}
    result = encrypt_env(env, PASS)
    assert result["KEY1"] != "val1"
    assert result["KEY2"] != "val2"


def test_decrypt_env_roundtrip():
    env = {"TOKEN": "abc123", "HOST": "localhost"}
    encrypted = encrypt_env(env, PASS, keys=["TOKEN"])
    decrypted = decrypt_env(encrypted, PASS, keys=["TOKEN"])
    assert decrypted == env


def test_encrypt_env_does_not_mutate_original():
    env = {"SECRET": "value"}
    encrypt_env(env, PASS)
    assert env["SECRET"] == "value"


def test_encrypt_env_skips_missing_keys():
    env = {"A": "1"}
    result = encrypt_env(env, PASS, keys=["A", "B"])
    assert "B" not in result
    assert result["A"] != "1"

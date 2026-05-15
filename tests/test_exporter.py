"""Tests for envpatch.exporter."""

import json
import pytest
from envpatch.exporter import (
    export_as_json,
    export_as_shell,
    export_as_toml,
    export_env,
    ExportError,
)


SAMPLE = {"APP_ENV": "production", "DB_HOST": "localhost", "PORT": "5432"}


# --- JSON ---

def test_export_json_is_valid_json():
    result = export_as_json(SAMPLE)
    parsed = json.loads(result)
    assert parsed == SAMPLE


def test_export_json_sorted_keys():
    result = export_as_json(SAMPLE)
    keys = list(json.loads(result).keys())
    assert keys == sorted(keys)


def test_export_json_indent():
    result = export_as_json(SAMPLE, indent=4)
    assert "    " in result


# --- Shell ---

def test_export_shell_contains_export():
    result = export_as_shell(SAMPLE)
    assert result.startswith("export ") or "\nexport " in result


def test_export_shell_no_export_keyword():
    result = export_as_shell(SAMPLE, export_keyword=False)
    assert "export" not in result


def test_export_shell_quoted_values():
    result = export_as_shell({"KEY": "hello world"})
    assert 'KEY="hello world"' in result


def test_export_shell_escapes_double_quotes():
    result = export_as_shell({"MSG": 'say "hi"'})
    assert '\\"' in result


def test_export_shell_sorted_keys():
    result = export_as_shell(SAMPLE)
    lines = [l for l in result.splitlines() if l.strip()]
    raw_keys = [l.split("=")[0].replace("export ", "").strip() for l in lines]
    assert raw_keys == sorted(raw_keys)


# --- TOML ---

def test_export_toml_has_env_header():
    result = export_as_toml(SAMPLE)
    assert result.startswith("[env]")


def test_export_toml_contains_keys():
    result = export_as_toml(SAMPLE)
    assert "APP_ENV" in result
    assert "DB_HOST" in result


def test_export_toml_values_quoted():
    result = export_as_toml({"X": "hello"})
    assert 'X = "hello"' in result


# --- export_env dispatch ---

def test_export_env_json():
    result = export_env(SAMPLE, "json")
    assert json.loads(result) == SAMPLE


def test_export_env_shell():
    result = export_env(SAMPLE, "shell")
    assert "PORT" in result


def test_export_env_toml():
    result = export_env(SAMPLE, "toml")
    assert "[env]" in result


def test_export_env_case_insensitive():
    result = export_env(SAMPLE, "JSON")
    assert json.loads(result) == SAMPLE


def test_export_env_unknown_format_raises():
    with pytest.raises(ExportError, match="Unsupported format"):
        export_env(SAMPLE, "xml")

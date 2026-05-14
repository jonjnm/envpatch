"""Tests for envpatch.auditor."""

import json
import os
import pytest
from envpatch.auditor import AuditEntry, record_entry, read_log, summarize_log


@pytest.fixture
def log_file(tmp_path):
    return str(tmp_path / "audit.log")


def make_entry(**kwargs):
    defaults = dict(
        operation="create",
        source_file="base.env",
        target_file="prod.env",
        keys_affected=["DB_HOST", "DB_PORT"],
        redacted=False,
    )
    defaults.update(kwargs)
    return AuditEntry(**defaults)


def test_entry_to_dict_has_expected_keys():
    entry = make_entry()
    d = entry.to_dict()
    assert "timestamp" in d
    assert d["operation"] == "create"
    assert d["keys_affected"] == ["DB_HOST", "DB_PORT"]
    assert d["redacted"] is False


def test_entry_str_contains_operation():
    entry = make_entry(operation="apply")
    assert "apply" in str(entry)


def test_entry_str_shows_redacted_note():
    entry = make_entry(redacted=True)
    assert "[redacted]" in str(entry)


def test_entry_str_truncates_long_key_list():
    keys = [f"KEY_{i}" for i in range(10)]
    entry = make_entry(keys_affected=keys)
    result = str(entry)
    assert "+5 more" in result


def test_record_entry_creates_file(log_file):
    entry = make_entry()
    record_entry(log_file, entry)
    assert os.path.exists(log_file)


def test_record_entry_writes_valid_json(log_file):
    entry = make_entry()
    record_entry(log_file, entry)
    with open(log_file) as fh:
        data = json.loads(fh.readline())
    assert data["operation"] == "create"


def test_record_multiple_entries_appends(log_file):
    record_entry(log_file, make_entry(operation="create"))
    record_entry(log_file, make_entry(operation="apply"))
    entries = read_log(log_file)
    assert len(entries) == 2
    assert entries[0].operation == "create"
    assert entries[1].operation == "apply"


def test_read_log_returns_empty_for_missing_file(tmp_path):
    result = read_log(str(tmp_path / "nonexistent.log"))
    assert result == []


def test_read_log_restores_all_fields(log_file):
    entry = make_entry(redacted=True, keys_affected=["SECRET_KEY"])
    record_entry(log_file, entry)
    loaded = read_log(log_file)[0]
    assert loaded.redacted is True
    assert loaded.keys_affected == ["SECRET_KEY"]
    assert loaded.source_file == "base.env"


def test_summarize_log_empty():
    result = summarize_log([])
    assert "No audit" in result


def test_summarize_log_shows_count():
    entries = [make_entry(), make_entry(operation="apply")]
    result = summarize_log(entries)
    assert "2 entries" in result


def test_summarize_log_lists_entries():
    entries = [make_entry(operation="show")]
    result = summarize_log(entries)
    assert "show" in result

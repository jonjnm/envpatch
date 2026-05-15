"""Tests for envpatch.reporter."""

import pytest
from unittest.mock import MagicMock
from envpatch.reporter import Report, build_diff_report, build_audit_report, _format_change
from envpatch.differ import EnvChange
from envpatch.auditor import AuditEntry
from datetime import datetime


@pytest.fixture
def added_change():
    return EnvChange(key="NEW_KEY", change_type="added", old_value=None, new_value="abc")


@pytest.fixture
def removed_change():
    return EnvChange(key="OLD_KEY", change_type="removed", old_value="xyz", new_value=None)


@pytest.fixture
def modified_change():
    return EnvChange(key="MOD_KEY", change_type="modified", old_value="v1", new_value="v2")


@pytest.fixture
def sample_entry():
    return AuditEntry(
        timestamp=datetime(2024, 1, 1, 12, 0, 0).isoformat(),
        operation="apply",
        user="ci",
        note="deployed patch",
    )


def test_report_str_contains_title():
    report = Report(title="My Report", sections=["section one"])
    assert "My Report" in str(report)


def test_report_str_contains_section_content():
    report = Report(title="T", sections=["hello world"])
    assert "hello world" in str(report)


def test_format_change_added_redacted(added_change):
    result = _format_change(added_change, redact=True)
    assert result.startswith("  +")
    assert "***" in result
    assert "abc" not in result


def test_format_change_added_not_redacted(added_change):
    result = _format_change(added_change, redact=False)
    assert "abc" in result


def test_format_change_removed(removed_change):
    result = _format_change(removed_change, redact=False)
    assert result.startswith("  -")
    assert "xyz" in result


def test_format_change_modified(modified_change):
    result = _format_change(modified_change, redact=False)
    assert result.startswith("  ~")
    assert "v1" in result
    assert "v2" in result


def test_build_diff_report_no_changes():
    report = build_diff_report([])
    assert "No changes" in str(report)


def test_build_diff_report_has_added_section(added_change):
    report = build_diff_report([added_change])
    assert "Added" in str(report)


def test_build_diff_report_has_removed_section(removed_change):
    report = build_diff_report([removed_change])
    assert "Removed" in str(report)


def test_build_diff_report_has_modified_section(modified_change):
    report = build_diff_report([modified_change])
    assert "Modified" in str(report)


def test_build_diff_report_summary_counts(added_change, removed_change, modified_change):
    report = build_diff_report([added_change, removed_change, modified_change])
    text = str(report)
    assert "1 added" in text
    assert "1 removed" in text
    assert "1 modified" in text


def test_build_audit_report_no_entries():
    report = build_audit_report([])
    assert "No audit entries" in str(report)


def test_build_audit_report_shows_entry(sample_entry):
    report = build_audit_report([sample_entry])
    text = str(report)
    assert "apply" in text


def test_build_audit_report_shows_total(sample_entry):
    report = build_audit_report([sample_entry, sample_entry])
    assert "Total entries: 2" in str(report)

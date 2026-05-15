"""Tests for envpatch.linter."""

import pytest
from envpatch.linter import lint_env, LintIssue


def test_clean_file_has_no_issues():
    text = "HOST=localhost\nPORT=5432\nDEBUG=false\n"
    result = lint_env(text)
    assert result.is_clean


def test_duplicate_key_flagged():
    text = "HOST=localhost\nHOST=remotehost\n"
    result = lint_env(text)
    codes = [i.code for i in result.issues]
    assert "W001" in codes


def test_duplicate_key_references_first_line():
    text = "KEY=a\nKEY=b\n"
    result = lint_env(text)
    issue = next(i for i in result.issues if i.code == "W001")
    assert "line 1" in issue.message


def test_missing_equals_flagged():
    text = "BADLINE\n"
    result = lint_env(text)
    codes = [i.code for i in result.issues]
    assert "E001" in codes


def test_empty_key_flagged():
    text = "=somevalue\n"
    result = lint_env(text)
    codes = [i.code for i in result.issues]
    assert "E002" in codes


def test_key_with_space_flagged():
    text = "MY KEY=value\n"
    result = lint_env(text)
    codes = [i.code for i in result.issues]
    assert "E003" in codes


def test_value_with_leading_whitespace_flagged():
    text = "KEY= value\n"
    result = lint_env(text)
    codes = [i.code for i in result.issues]
    assert "W002" in codes


def test_value_with_trailing_whitespace_flagged():
    text = "KEY=value \n"
    result = lint_env(text)
    codes = [i.code for i in result.issues]
    assert "W002" in codes


def test_placeholder_todo_flagged():
    text = "SECRET=todo\n"
    result = lint_env(text)
    codes = [i.code for i in result.issues]
    assert "W003" in codes


def test_placeholder_changeme_flagged():
    text = "PASSWORD=changeme\n"
    result = lint_env(text)
    codes = [i.code for i in result.issues]
    assert "W003" in codes


def test_comments_ignored():
    text = "# this is a comment\n# another comment\n"
    result = lint_env(text)
    assert result.is_clean


def test_blank_lines_ignored():
    text = "\n\n   \n"
    result = lint_env(text)
    assert result.is_clean


def test_summary_clean():
    result = lint_env("KEY=value\n")
    assert result.summary() == "No issues found."


def test_summary_shows_issues():
    result = lint_env("BADLINE\n")
    assert "E001" in result.summary()


def test_issue_str_contains_line_and_code():
    issue = LintIssue(line=3, key="FOO", code="W001", message="dup")
    s = str(issue)
    assert "3" in s
    assert "W001" in s

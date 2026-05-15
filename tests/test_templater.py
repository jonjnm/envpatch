"""Tests for envpatch.templater module."""

import pytest

from envpatch.templater import TemplateError, list_placeholders, render_template


# --- render_template ---

def test_simple_placeholder_replaced():
    result = render_template("Hello {{NAME}}", {"NAME": "world"})
    assert result == "Hello world"


def test_multiple_placeholders_replaced():
    result = render_template("{{HOST}}:{{PORT}}", {"HOST": "localhost", "PORT": "5432"})
    assert result == "localhost:5432"


def test_placeholder_with_spaces_inside_braces():
    result = render_template("{{ KEY }}", {"KEY": "value"})
    assert result == "value"


def test_missing_key_left_as_is_non_strict():
    result = render_template("{{MISSING}}", {}, strict=False)
    assert result == "{{MISSING}}"


def test_missing_key_raises_in_strict_mode():
    with pytest.raises(TemplateError, match="MISSING"):
        render_template("{{MISSING}}", {}, strict=True)


def test_no_placeholders_returns_template_unchanged():
    tmpl = "just plain text\nno substitution"
    assert render_template(tmpl, {"KEY": "val"}) == tmpl


def test_same_placeholder_replaced_multiple_times():
    result = render_template("{{X}} and {{X}}", {"X": "42"})
    assert result == "42 and 42"


def test_empty_env_non_strict_leaves_placeholders():
    result = render_template("{{A}} {{B}}", {})
    assert result == "{{A}} {{B}}"


def test_value_with_special_characters():
    result = render_template("DB={{URL}}", {"URL": "postgres://user:pass@host/db"})
    assert result == "DB=postgres://user:pass@host/db"


# --- list_placeholders ---

def test_list_placeholders_returns_sorted_unique():
    tmpl = "{{B}} {{A}} {{B}}"
    assert list_placeholders(tmpl) == ["A", "B"]


def test_list_placeholders_empty_when_none_found():
    assert list_placeholders("no placeholders here") == []


def test_list_placeholders_with_spaces_in_braces():
    tmpl = "{{ FOO }} and {{BAR}}"
    assert list_placeholders(tmpl) == ["BAR", "FOO"]


def test_render_template_file_writes_output(tmp_path):
    from envpatch.templater import render_template_file

    tmpl = tmp_path / "app.env.tmpl"
    tmpl.write_text("HOST={{HOST}}\nPORT={{PORT}}\n")
    out = tmp_path / "app.env"

    rendered = render_template_file(str(tmpl), {"HOST": "localhost", "PORT": "8080"}, output_path=str(out))

    assert rendered == "HOST=localhost\nPORT=8080\n"
    assert out.read_text() == "HOST=localhost\nPORT=8080\n"

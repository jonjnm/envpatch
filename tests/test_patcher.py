"""Tests for envpatch.patcher module."""

import pytest
from pathlib import Path

from envpatch.patcher import write_patch, read_patch, create_patch, apply_patch, PATCH_HEADER
from envpatch.differ import EnvChange


@pytest.fixture
def tmp_env_base(tmp_path):
    f = tmp_path / "base.env"
    f.write_text("HOST=localhost\nPORT=5432\nDEBUG=true\n")
    return f


@pytest.fixture
def tmp_env_target(tmp_path):
    f = tmp_path / "target.env"
    f.write_text("HOST=prod.example.com\nPORT=5432\nNEW_KEY=hello\n")
    return f


def test_write_patch_creates_file(tmp_path):
    patch_path = tmp_path / "changes.patch"
    changes = [
        EnvChange(key="HOST", change_type="modified", new_value="prod.example.com"),
        EnvChange(key="NEW_KEY", change_type="added", new_value="hello"),
        EnvChange(key="DEBUG", change_type="removed"),
    ]
    write_patch(changes, patch_path)
    assert patch_path.exists()
    content = patch_path.read_text()
    assert PATCH_HEADER in content


def test_write_patch_format(tmp_path):
    patch_path = tmp_path / "changes.patch"
    changes = [
        EnvChange(key="FOO", change_type="added", new_value="bar"),
        EnvChange(key="OLD", change_type="removed"),
    ]
    write_patch(changes, patch_path)
    lines = patch_path.read_text().splitlines()
    assert "+FOO=bar" in lines
    assert "-OLD" in lines


def test_read_patch_added(tmp_path):
    patch_path = tmp_path / "test.patch"
    patch_path.write_text("# envpatch\n+NEW_KEY=value\n")
    changes = read_patch(patch_path)
    assert len(changes) == 1
    assert changes[0].change_type == "added"
    assert changes[0].key == "NEW_KEY"
    assert changes[0].new_value == "value"


def test_read_patch_removed(tmp_path):
    patch_path = tmp_path / "test.patch"
    patch_path.write_text("# envpatch\n-OLD_KEY\n")
    changes = read_patch(patch_path)
    assert len(changes) == 1
    assert changes[0].change_type == "removed"
    assert changes[0].key == "OLD_KEY"


def test_read_patch_modified(tmp_path):
    patch_path = tmp_path / "test.patch"
    patch_path.write_text("# envpatch\n-HOST\n+HOST=newvalue\n")
    changes = read_patch(patch_path)
    assert len(changes) == 1
    assert changes[0].change_type == "modified"
    assert changes[0].new_value == "newvalue"


def test_read_patch_invalid_header(tmp_path):
    patch_path = tmp_path / "bad.patch"
    patch_path.write_text("NOT A PATCH\n+KEY=val\n")
    with pytest.raises(ValueError, match="Not a valid envpatch file"):
        read_patch(patch_path)


def test_create_patch_roundtrip(tmp_path, tmp_env_base, tmp_env_target):
    patch_path = tmp_path / "out.patch"
    changes = create_patch(tmp_env_base, tmp_env_target, patch_path)
    assert patch_path.exists()
    keys = {c.key for c in changes}
    assert "HOST" in keys
    assert "DEBUG" in keys
    assert "NEW_KEY" in keys


def test_apply_patch_produces_merged_env(tmp_path, tmp_env_base, tmp_env_target):
    patch_path = tmp_path / "out.patch"
    output_path = tmp_path / "result.env"
    create_patch(tmp_env_base, tmp_env_target, patch_path)
    result = apply_patch(tmp_env_base, patch_path, output_path)
    assert result.get("HOST") == "prod.example.com"
    assert result.get("PORT") == "5432"
    assert "DEBUG" not in result
    assert result.get("NEW_KEY") == "hello"
    assert output_path.exists()

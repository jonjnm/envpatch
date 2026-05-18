import pytest
from envpatch.differ import EnvChange
from envpatch.differ_summary import (
    DiffSummary,
    build_diff_summary,
    changes_by_key,
)


@pytest.fixture
def sample_changes():
    return [
        EnvChange(key="NEW_KEY", change_type="added", old_value=None, new_value="hello"),
        EnvChange(key="OLD_KEY", change_type="removed", old_value="bye", new_value=None),
        EnvChange(key="MOD_KEY", change_type="modified", old_value="a", new_value="b"),
    ]


def test_build_diff_summary_added(sample_changes):
    result = build_diff_summary(sample_changes)
    assert len(result.added) == 1
    assert result.added[0].key == "NEW_KEY"


def test_build_diff_summary_removed(sample_changes):
    result = build_diff_summary(sample_changes)
    assert len(result.removed) == 1
    assert result.removed[0].key == "OLD_KEY"


def test_build_diff_summary_modified(sample_changes):
    result = build_diff_summary(sample_changes)
    assert len(result.modified) == 1
    assert result.modified[0].key == "MOD_KEY"


def test_total_count(sample_changes):
    result = build_diff_summary(sample_changes)
    assert result.total == 3


def test_is_clean_false(sample_changes):
    result = build_diff_summary(sample_changes)
    assert result.is_clean is False


def test_is_clean_true():
    result = build_diff_summary([])
    assert result.is_clean is True


def test_summary_string_no_changes():
    result = build_diff_summary([])
    assert result.summary() == "No differences found."


def test_summary_string_with_changes(sample_changes):
    result = build_diff_summary(sample_changes)
    text = result.summary()
    assert "added" in text
    assert "removed" in text
    assert "modified" in text
    assert "3 total" in text


def test_to_dict_keys(sample_changes):
    result = build_diff_summary(sample_changes)
    d = result.to_dict()
    assert "added" in d
    assert "removed" in d
    assert "modified" in d
    assert d["total"] == 3


def test_to_dict_values(sample_changes):
    result = build_diff_summary(sample_changes)
    d = result.to_dict()
    assert "NEW_KEY" in d["added"]
    assert "OLD_KEY" in d["removed"]
    assert "MOD_KEY" in d["modified"]


def test_changes_by_key(sample_changes):
    mapping = changes_by_key(sample_changes)
    assert "NEW_KEY" in mapping
    assert mapping["MOD_KEY"].new_value == "b"


def test_changes_by_key_empty():
    assert changes_by_key([]) == {}

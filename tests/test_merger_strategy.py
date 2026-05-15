"""Tests for envpatch.merger_strategy."""

import pytest
from envpatch.merger_strategy import (
    Strategy,
    MergeConflict,
    merge_with_strategy,
    list_conflicts,
)


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
INCOMING = {"HOST": "prod.example.com", "PORT": "5432", "NEW_KEY": "hello"}


def test_theirs_overwrites_on_conflict():
    result = merge_with_strategy(BASE, INCOMING, Strategy.THEIRS)
    assert result["HOST"] == "prod.example.com"


def test_theirs_keeps_unchanged_keys():
    result = merge_with_strategy(BASE, INCOMING, Strategy.THEIRS)
    assert result["DEBUG"] == "true"


def test_theirs_adds_new_keys():
    result = merge_with_strategy(BASE, INCOMING, Strategy.THEIRS)
    assert result["NEW_KEY"] == "hello"


def test_ours_keeps_base_on_conflict():
    result = merge_with_strategy(BASE, INCOMING, Strategy.OURS)
    assert result["HOST"] == "localhost"


def test_ours_still_adds_new_keys():
    result = merge_with_strategy(BASE, INCOMING, Strategy.OURS)
    assert result["NEW_KEY"] == "hello"


def test_skip_leaves_conflicting_key_unchanged():
    result = merge_with_strategy(BASE, INCOMING, Strategy.SKIP)
    assert result["HOST"] == "localhost"


def test_skip_still_adds_new_keys():
    result = merge_with_strategy(BASE, INCOMING, Strategy.SKIP)
    assert result["NEW_KEY"] == "hello"


def test_prompt_raises_on_conflict():
    with pytest.raises(MergeConflict) as exc_info:
        merge_with_strategy(BASE, INCOMING, Strategy.PROMPT)
    assert exc_info.value.key == "HOST"
    assert exc_info.value.base_value == "localhost"
    assert exc_info.value.incoming_value == "prod.example.com"


def test_prompt_does_not_raise_when_no_conflict():
    no_conflict = {"NEW_KEY": "hello"}
    result = merge_with_strategy(BASE, no_conflict, Strategy.PROMPT)
    assert result["NEW_KEY"] == "hello"


def test_protected_keys_never_overwritten():
    result = merge_with_strategy(BASE, INCOMING, Strategy.THEIRS, protected_keys=["HOST"])
    assert result["HOST"] == "localhost"


def test_protected_key_not_added_from_incoming():
    incoming = {"SUPER_SECRET": "value"}
    result = merge_with_strategy(BASE, incoming, Strategy.THEIRS, protected_keys=["SUPER_SECRET"])
    assert "SUPER_SECRET" not in result


def test_no_mutation_of_base():
    original = dict(BASE)
    merge_with_strategy(BASE, INCOMING, Strategy.THEIRS)
    assert BASE == original


def test_list_conflicts_finds_differing_keys():
    conflicts = list_conflicts(BASE, INCOMING)
    assert "HOST" in conflicts


def test_list_conflicts_excludes_matching_keys():
    conflicts = list_conflicts(BASE, INCOMING)
    assert "PORT" not in conflicts


def test_list_conflicts_excludes_new_keys():
    conflicts = list_conflicts(BASE, INCOMING)
    assert "NEW_KEY" not in conflicts


def test_list_conflicts_empty_when_no_overlap():
    conflicts = list_conflicts(BASE, {"BRAND_NEW": "x"})
    assert conflicts == []

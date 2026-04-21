"""Tests for domain normalization rules."""

from __future__ import annotations

import pytest

from app.domain.normalization import are_equivalent, normalize_for_comparison, normalize_with_raw


def test_normalize_for_comparison_trims_and_casefolds() -> None:
    assert normalize_for_comparison("  Alice  ") == "alice"


def test_normalize_for_comparison_applies_nfkc_for_fullwidth() -> None:
    assert normalize_for_comparison("ＡＢｃ１２３") == "abc123"


def test_normalize_for_comparison_collapses_whitespace_and_control_chars() -> None:
    assert normalize_for_comparison(" A\t\nB\r\nC ") == "a b c"


def test_normalize_for_comparison_rejects_none_or_empty_result() -> None:
    with pytest.raises(ValueError):
        normalize_for_comparison(None)

    with pytest.raises(ValueError):
        normalize_for_comparison(" \t\n ")


def test_normalize_with_raw_keeps_display_text_and_optional_normalized() -> None:
    normalized = normalize_with_raw("  Alice\n")
    assert normalized.raw_text == "  Alice\n"
    assert normalized.normalized_text == "alice"

    empty_normalized = normalize_with_raw("\t\n")
    assert empty_normalized.raw_text == "\t\n"
    assert empty_normalized.normalized_text is None


def test_are_equivalent_uses_normalized_comparison() -> None:
    assert are_equivalent("Ａｌｉｃｅ", " alice ") is True
    assert are_equivalent("Alice", "Bob") is False
    assert are_equivalent(None, "") is False

"""Tests for UI datetime display helpers."""

from __future__ import annotations

from datetime import UTC, datetime

from app.ui.datetime_display import format_datetime_display


def test_format_datetime_display_formats_iso_string_with_z() -> None:
    assert format_datetime_display("2026-01-02T03:04:05Z") == "2026/01/02 03:04:05"


def test_format_datetime_display_formats_iso_string_with_offset() -> None:
    assert (
        format_datetime_display("2026-01-02T12:34:56+09:00")
        == "2026/01/02 12:34:56"
    )


def test_format_datetime_display_formats_space_separated_iso_string() -> None:
    assert (
        format_datetime_display("2026-01-02 03:04:05.987654")
        == "2026/01/02 03:04:05"
    )


def test_format_datetime_display_formats_datetime() -> None:
    value = datetime(2026, 1, 2, 3, 4, 5, 987654, tzinfo=UTC)

    assert format_datetime_display(value) == "2026/01/02 03:04:05"


def test_format_datetime_display_handles_none() -> None:
    assert format_datetime_display(None) == ""
    assert format_datetime_display(None, none_text="不明") == "不明"


def test_format_datetime_display_keeps_invalid_string_safe() -> None:
    assert format_datetime_display(" not-a-datetime ") == "not-a-datetime"

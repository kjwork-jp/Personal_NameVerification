from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.ui.datetime_display import format_datetime_display


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026-06-03T04:05:06Z", "2026/06/03 04:05:06"),
        ("2026-06-03T04:05:06+09:00", "2026/06/03 04:05:06"),
        ("2026-06-03 04:05:06", "2026/06/03 04:05:06"),
        ("2026-06-03", "2026/06/03 00:00:00"),
    ],
)
def test_format_datetime_display_formats_iso_strings(value: str, expected: str) -> None:
    assert format_datetime_display(value) == expected


def test_format_datetime_display_formats_datetime() -> None:
    value = datetime(2026, 6, 3, 4, 5, 6, 123456, tzinfo=UTC)

    assert format_datetime_display(value) == "2026/06/03 04:05:06"


def test_format_datetime_display_returns_empty_string_for_none() -> None:
    assert format_datetime_display(None) == ""


@pytest.mark.parametrize("value", ["", "not-a-date", "2026-99-99T00:00:00Z"])
def test_format_datetime_display_returns_fallback_for_invalid_strings(value: str) -> None:
    assert format_datetime_display(value, fallback="不明") == "不明"


def test_format_datetime_display_returns_fallback_for_unsupported_values() -> None:
    assert format_datetime_display(12345, fallback="不明") == "不明"  # type: ignore[arg-type]

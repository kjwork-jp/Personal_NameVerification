"""Common UI datetime display formatting helpers."""

from __future__ import annotations

from datetime import datetime

DISPLAY_DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S"

DatetimeDisplayValue = datetime | str | None


def format_datetime_display(value: DatetimeDisplayValue, *, none_text: str = "") -> str:
    """Return a safe UI display string for datetime-like values."""

    if value is None:
        return none_text
    if isinstance(value, datetime):
        return value.strftime(DISPLAY_DATETIME_FORMAT)
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return none_text
        parsed = _parse_iso_datetime(stripped)
        if parsed is None:
            return stripped
        return parsed.strftime(DISPLAY_DATETIME_FORMAT)
    return str(value)


def _parse_iso_datetime(value: str) -> datetime | None:
    normalized = value
    if normalized.endswith(("Z", "z")):
        normalized = f"{normalized[:-1]}+00:00"
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None

"""UI formatting helpers for datetime values."""

from __future__ import annotations

from datetime import datetime

DISPLAY_DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S"


def format_datetime_display(value: datetime | str | None, *, fallback: str = "") -> str:
    """Return a safe UI datetime string in YYYY/MM/DD HH:MM:SS format."""

    parsed = _coerce_datetime(value)
    if parsed is None:
        return fallback

    try:
        return parsed.strftime(DISPLAY_DATETIME_FORMAT)
    except (OSError, ValueError):
        return fallback


def _coerce_datetime(value: object) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return _parse_iso_datetime(value)
    return None


def _parse_iso_datetime(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None

    if text.upper().endswith("Z"):
        text = f"{text[:-1]}+00:00"

    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None

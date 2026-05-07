"""UI formatting helpers for public_id values."""

from __future__ import annotations


def short_public_id(public_id: str | None) -> str:
    """Return a compact public_id label for dense UI areas."""

    if not public_id:
        return "未採番"
    if len(public_id) <= 12:
        return public_id
    return f"{public_id[:8]}…{public_id[-4:]}"


def public_id_detail(public_id: str | None) -> str:
    """Return a full public_id label for detail text areas."""

    return public_id or "未採番"

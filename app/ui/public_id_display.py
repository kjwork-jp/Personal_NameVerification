"""UI formatting helpers for public_id values."""

from __future__ import annotations


def short_public_id(public_id: str | None) -> str:
    """Return public_id without truncation for release/UAT auditability."""

    return public_id or "未採番"


def public_id_detail(public_id: str | None) -> str:
    """Return a full public_id label for detail text areas and tooltips."""

    return public_id or "未採番"

"""String normalization rules for comparison keys."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

_SPACE_LIKE_PATTERN = re.compile(r"\s+")
_CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x1F\x7F]")


@dataclass(frozen=True)
class NormalizedText:
    """Container for raw display text and normalized comparison text."""

    raw_text: str
    normalized_text: str | None


def normalize_for_comparison(value: str | None) -> str:
    """Normalize input text for comparison and unique-key usage.

    Raises:
        ValueError: If input is None or normalization results in an empty string.
    """
    if value is None:
        raise ValueError("value must not be None")

    normalized = _normalize_text(value)
    if not normalized:
        raise ValueError("normalized value is empty")
    return normalized


def normalize_with_raw(value: str | None) -> NormalizedText:
    """Return raw text for display and normalized text for comparison."""
    raw_text = value or ""
    normalized = _normalize_text(raw_text)
    return NormalizedText(raw_text=raw_text, normalized_text=normalized or None)


def are_equivalent(left: str | None, right: str | None) -> bool:
    """Check whether two values are equivalent under normalization rules."""
    left_norm = normalize_with_raw(left).normalized_text
    right_norm = normalize_with_raw(right).normalized_text
    return left_norm is not None and left_norm == right_norm


def _normalize_text(value: str) -> str:
    control_cleaned = _CONTROL_CHAR_PATTERN.sub(" ", value)
    normalized = unicodedata.normalize("NFKC", control_cleaned)
    collapsed = _SPACE_LIKE_PATTERN.sub(" ", normalized).strip()
    return collapsed.casefold()

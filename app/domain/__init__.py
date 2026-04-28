"""Domain layer package (entities, rules, and validations)."""

from .normalization import (
    NormalizedText,
    are_equivalent,
    normalize_for_comparison,
    normalize_with_raw,
)

__all__ = [
    "NormalizedText",
    "are_equivalent",
    "normalize_for_comparison",
    "normalize_with_raw",
]

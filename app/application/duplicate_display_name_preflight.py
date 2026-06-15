"""Preflight checks for future display-name uniqueness constraints."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any

from app.domain.normalization import normalize_with_raw


@dataclass(frozen=True)
class DuplicateDisplayNameGroup:
    """One normalized active display-name group that would block a unique constraint."""

    entity_type: str
    normalized_key: str
    ids: tuple[int, ...]
    display_names: tuple[str, ...]
    title_id: int | None = None


@dataclass(frozen=True)
class DuplicateDisplayNamePreflightReport:
    """Preflight result for active title/subtitle display-name duplicates."""

    title_duplicates: tuple[DuplicateDisplayNameGroup, ...]
    subtitle_duplicates: tuple[DuplicateDisplayNameGroup, ...]

    @property
    def has_blockers(self) -> bool:
        return bool(self.title_duplicates or self.subtitle_duplicates)

    @property
    def blocker_count(self) -> int:
        return len(self.title_duplicates) + len(self.subtitle_duplicates)


def inspect_duplicate_display_names(
    connection: sqlite3.Connection,
) -> DuplicateDisplayNamePreflightReport:
    """Inspect active title/subtitle display names before adding DB constraints.

    This intentionally reports instead of mutating data. Deleted rows and legacy blank
    display names are ignored so cleanup can stay explicit and reversible.
    """
    return DuplicateDisplayNamePreflightReport(
        title_duplicates=_find_title_duplicates(connection),
        subtitle_duplicates=_find_subtitle_duplicates(connection),
    )


def _find_title_duplicates(
    connection: sqlite3.Connection,
) -> tuple[DuplicateDisplayNameGroup, ...]:
    rows = connection.execute(
        """
        SELECT id, title_name
        FROM titles
        WHERE deleted_at IS NULL
        ORDER BY id
        """
    ).fetchall()
    groups: dict[str, list[tuple[int, str]]] = {}
    for row in rows:
        row_id = int(_row_value(row, "id", 0))
        display_name = str(_row_value(row, "title_name", 1))
        normalized_key = normalize_with_raw(display_name).normalized_text
        if normalized_key is None:
            continue
        groups.setdefault(normalized_key, []).append((row_id, display_name))
    return tuple(
        DuplicateDisplayNameGroup(
            entity_type="title",
            normalized_key=normalized_key,
            ids=tuple(item[0] for item in items),
            display_names=tuple(item[1] for item in items),
        )
        for normalized_key, items in sorted(groups.items())
        if len(items) > 1
    )


def _find_subtitle_duplicates(
    connection: sqlite3.Connection,
) -> tuple[DuplicateDisplayNameGroup, ...]:
    rows = connection.execute(
        """
        SELECT id, title_id, subtitle_name
        FROM subtitles
        WHERE deleted_at IS NULL
        ORDER BY title_id, id
        """
    ).fetchall()
    groups: dict[tuple[int, str], list[tuple[int, str]]] = {}
    for row in rows:
        row_id = int(_row_value(row, "id", 0))
        title_id = int(_row_value(row, "title_id", 1))
        display_name = str(_row_value(row, "subtitle_name", 2))
        normalized_key = normalize_with_raw(display_name).normalized_text
        if normalized_key is None:
            continue
        groups.setdefault((title_id, normalized_key), []).append((row_id, display_name))
    return tuple(
        DuplicateDisplayNameGroup(
            entity_type="subtitle",
            normalized_key=normalized_key,
            title_id=title_id,
            ids=tuple(item[0] for item in items),
            display_names=tuple(item[1] for item in items),
        )
        for (title_id, normalized_key), items in sorted(groups.items())
        if len(items) > 1
    )


def _row_value(row: Any, key: str, index: int) -> Any:
    try:
        return row[key]
    except (TypeError, IndexError):
        return row[index]

"""Detect duplicate candidates for names, titles, and subtitles.

This script is intentionally read-only. It reports candidate duplicate groups
without changing data or adding database constraints.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from app.domain.normalization import normalize_with_raw

EntityKind = Literal["names", "titles", "subtitles"]
KeyType = Literal["display", "normalized"]

ENTITY_KINDS: tuple[EntityKind, ...] = ("names", "titles", "subtitles")
KEY_TYPES: tuple[KeyType, ...] = ("display", "normalized")


@dataclass(frozen=True)
class EntityRecord:
    """Single entity row used by duplicate detection."""

    entity_kind: EntityKind
    entity_id: int
    display_value: str
    normalized_value: str | None = None
    public_id: str | None = None
    deleted_at: str | None = None
    context: str | None = None


@dataclass(frozen=True)
class DuplicateGroup:
    """Duplicate candidate group sharing the same comparison key."""

    entity_kind: EntityKind
    key_type: KeyType
    key_value: str
    records: tuple[EntityRecord, ...]


def find_duplicate_groups(
    records: list[EntityRecord],
    *,
    key_types: tuple[KeyType, ...] = KEY_TYPES,
) -> list[DuplicateGroup]:
    """Group records by selected keys and return groups with more than one row."""

    groups: list[DuplicateGroup] = []
    for entity_kind in ENTITY_KINDS:
        entity_records = [record for record in records if record.entity_kind == entity_kind]
        for key_type in key_types:
            grouped: dict[str, list[EntityRecord]] = {}
            for record in entity_records:
                key_value = _key_value(record, key_type)
                if key_value is None:
                    continue
                grouped.setdefault(key_value, []).append(record)

            for key_value, group_records in grouped.items():
                if len(group_records) < 2:
                    continue
                groups.append(
                    DuplicateGroup(
                        entity_kind=entity_kind,
                        key_type=key_type,
                        key_value=key_value,
                        records=tuple(sorted(group_records, key=lambda item: item.entity_id)),
                    )
                )

    return sorted(
        groups,
        key=lambda group: (
            group.entity_kind,
            group.key_type,
            group.key_value.casefold(),
            group.key_value,
        ),
    )


def fetch_entity_records(
    connection: sqlite3.Connection,
    *,
    entity_kinds: tuple[EntityKind, ...] = ENTITY_KINDS,
    include_deleted: bool = False,
) -> list[EntityRecord]:
    """Fetch entity rows from SQLite for duplicate detection."""

    records: list[EntityRecord] = []
    for entity_kind in entity_kinds:
        if entity_kind == "names":
            records.extend(_fetch_names(connection, include_deleted=include_deleted))
        elif entity_kind == "titles":
            records.extend(_fetch_titles(connection, include_deleted=include_deleted))
        elif entity_kind == "subtitles":
            records.extend(_fetch_subtitles(connection, include_deleted=include_deleted))
        else:
            raise ValueError(f"unsupported entity kind: {entity_kind}")
    return records


def build_summary(
    *,
    db_path: Path,
    include_deleted: bool,
    groups: list[DuplicateGroup],
    entity_kinds: tuple[EntityKind, ...],
    key_types: tuple[KeyType, ...],
    max_records_per_group: int = 20,
) -> str:
    """Build a readable duplicate detection summary for stdout."""

    lines = [
        "Duplicate entity candidates",
        f"DB: {db_path}",
        f"Scope: {'active and deleted rows' if include_deleted else 'active rows only'}",
        f"Entities: {', '.join(entity_kinds)}",
        f"Keys: {', '.join(key_types)}",
        "",
        "Summary",
    ]

    for entity_kind in entity_kinds:
        for key_type in key_types:
            matching = [
                group
                for group in groups
                if group.entity_kind == entity_kind and group.key_type == key_type
            ]
            duplicate_rows = sum(len(group.records) for group in matching)
            lines.append(
                f"- {entity_kind}/{key_type}: "
                f"{len(matching)} group(s), {duplicate_rows} row(s)"
            )

    if not groups:
        lines.extend(["", "No duplicate candidates found."])
        return "\n".join(lines)

    lines.extend(["", "Details"])
    for group in groups:
        lines.append(
            f"[{group.entity_kind}/{group.key_type}] "
            f"key={group.key_value!r} ({len(group.records)} rows)"
        )
        visible_records = group.records[:max_records_per_group]
        for record in visible_records:
            details = [
                f"id={record.entity_id}",
                f"display={record.display_value!r}",
            ]
            if record.normalized_value is not None:
                details.append(f"normalized={record.normalized_value!r}")
            if record.public_id is not None:
                details.append(f"public_id={record.public_id}")
            if record.deleted_at is not None:
                details.append(f"deleted_at={record.deleted_at}")
            if record.context is not None:
                details.append(record.context)
            lines.append(f"  - {'; '.join(details)}")
        remaining = len(group.records) - len(visible_records)
        if remaining > 0:
            lines.append(f"  - ... {remaining} more row(s)")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Detect duplicate candidates in NameVerification SQLite data."
    )
    parser.add_argument(
        "db_path",
        nargs="?",
        default=os.environ.get("NAMEVERIFICATION_DB_PATH", "nameverification.db"),
        help=(
            "SQLite DB path. Defaults to NAMEVERIFICATION_DB_PATH, "
            "then ./nameverification.db."
        ),
    )
    parser.add_argument(
        "--entity",
        choices=ENTITY_KINDS,
        action="append",
        dest="entities",
        help="Entity type to scan. Repeatable. Defaults to all.",
    )
    parser.add_argument(
        "--key",
        choices=KEY_TYPES,
        action="append",
        dest="keys",
        help="Comparison key to use. Repeatable. Defaults to display and normalized.",
    )
    parser.add_argument(
        "--include-deleted",
        action="store_true",
        help="Include logically deleted rows in detection.",
    )
    parser.add_argument(
        "--max-records-per-group",
        type=int,
        default=20,
        help="Maximum rows shown per duplicate group in stdout.",
    )
    args = parser.parse_args(argv)

    db_path = Path(args.db_path).expanduser()
    entity_kinds = tuple(args.entities) if args.entities else ENTITY_KINDS
    key_types = tuple(args.keys) if args.keys else KEY_TYPES

    with _connect_readonly(db_path) as connection:
        records = fetch_entity_records(
            connection,
            entity_kinds=entity_kinds,
            include_deleted=args.include_deleted,
        )
    groups = find_duplicate_groups(records, key_types=key_types)
    print(
        build_summary(
            db_path=db_path,
            include_deleted=args.include_deleted,
            groups=groups,
            entity_kinds=entity_kinds,
            key_types=key_types,
            max_records_per_group=args.max_records_per_group,
        )
    )
    return 0


def _connect_readonly(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(f"SQLite DB not found: {db_path}")
    uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def _fetch_names(connection: sqlite3.Connection, *, include_deleted: bool) -> list[EntityRecord]:
    if not _table_exists(connection, "names"):
        return []
    columns = _table_columns(connection, "names")
    public_id_select = "public_id" if "public_id" in columns else "NULL AS public_id"
    normalized_select = (
        "normalized_name" if "normalized_name" in columns else "NULL AS normalized_name"
    )
    deleted_at_select = "deleted_at" if "deleted_at" in columns else "NULL AS deleted_at"
    where_clause = (
        "" if include_deleted or "deleted_at" not in columns else "WHERE deleted_at IS NULL"
    )
    rows = connection.execute(
        f"""
        SELECT id, {public_id_select}, raw_name, {normalized_select}, {deleted_at_select}
        FROM names
        {where_clause}
        ORDER BY raw_name ASC, id ASC
        """
    ).fetchall()
    return [
        EntityRecord(
            entity_kind="names",
            entity_id=int(row["id"]),
            public_id=row["public_id"],
            display_value=row["raw_name"],
            normalized_value=row["normalized_name"] or _normalize_optional(row["raw_name"]),
            deleted_at=row["deleted_at"],
        )
        for row in rows
    ]


def _fetch_titles(connection: sqlite3.Connection, *, include_deleted: bool) -> list[EntityRecord]:
    if not _table_exists(connection, "titles"):
        return []
    columns = _table_columns(connection, "titles")
    public_id_select = "public_id" if "public_id" in columns else "NULL AS public_id"
    deleted_at_select = "deleted_at" if "deleted_at" in columns else "NULL AS deleted_at"
    where_clause = (
        "" if include_deleted or "deleted_at" not in columns else "WHERE deleted_at IS NULL"
    )
    rows = connection.execute(
        f"""
        SELECT id, {public_id_select}, title_name, {deleted_at_select}
        FROM titles
        {where_clause}
        ORDER BY title_name ASC, id ASC
        """
    ).fetchall()
    return [
        EntityRecord(
            entity_kind="titles",
            entity_id=int(row["id"]),
            public_id=row["public_id"],
            display_value=row["title_name"],
            normalized_value=_normalize_optional(row["title_name"]),
            deleted_at=row["deleted_at"],
        )
        for row in rows
    ]


def _fetch_subtitles(
    connection: sqlite3.Connection, *, include_deleted: bool
) -> list[EntityRecord]:
    if not _table_exists(connection, "subtitles"):
        return []
    columns = _table_columns(connection, "subtitles")
    public_id_select = "s.public_id" if "public_id" in columns else "NULL AS public_id"
    deleted_at_select = "s.deleted_at" if "deleted_at" in columns else "NULL AS deleted_at"
    where_clause = (
        "" if include_deleted or "deleted_at" not in columns else "WHERE s.deleted_at IS NULL"
    )
    title_join = (
        "LEFT JOIN titles t ON t.id = s.title_id"
        if _table_exists(connection, "titles")
        else ""
    )
    title_name_select = "t.title_name" if title_join else "NULL AS title_name"
    rows = connection.execute(
        f"""
        SELECT
            s.id,
            {public_id_select},
            s.title_id,
            s.subtitle_code,
            s.subtitle_name,
            {deleted_at_select},
            {title_name_select}
        FROM subtitles s
        {title_join}
        {where_clause}
        ORDER BY s.subtitle_name ASC, s.id ASC
        """
    ).fetchall()
    return [
        EntityRecord(
            entity_kind="subtitles",
            entity_id=int(row["id"]),
            public_id=row["public_id"],
            display_value=row["subtitle_name"],
            normalized_value=_normalize_optional(row["subtitle_name"]),
            deleted_at=row["deleted_at"],
            context=_subtitle_context(row),
        )
        for row in rows
    ]


def _key_value(record: EntityRecord, key_type: KeyType) -> str | None:
    if key_type == "display":
        return record.display_value
    if key_type == "normalized":
        return record.normalized_value
    raise ValueError(f"unsupported key type: {key_type}")


def _normalize_optional(value: str | None) -> str | None:
    return normalize_with_raw(value).normalized_text


def _subtitle_context(row: sqlite3.Row) -> str:
    parts = [f"title_id={row['title_id']}", f"code={row['subtitle_code']}"]
    if row["title_name"]:
        parts.append(f"title={row['title_name']!r}")
    return "; ".join(parts)


def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    row = connection.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table' AND name = ?
        """,
        (table_name,),
    ).fetchone()
    return row is not None


def _table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    return {
        str(row["name"])
        for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    }


if __name__ == "__main__":
    raise SystemExit(main())

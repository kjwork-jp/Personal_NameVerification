"""Schema definition tests for SQLite bootstrap."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.infrastructure.db import apply_schema


def _table_names(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%';"
    ).fetchall()
    return {row[0] for row in rows}


def test_schema_creates_required_tables() -> None:
    conn = sqlite3.connect(":memory:")
    apply_schema(conn)

    assert _table_names(conn) == {
        "change_logs",
        "name_subtitle_links",
        "name_title_links",
        "names",
        "subtitles",
        "titles",
    }


def test_subtitles_and_links_have_foreign_keys() -> None:
    conn = sqlite3.connect(":memory:")
    apply_schema(conn)

    subtitle_fks = conn.execute("PRAGMA foreign_key_list(subtitles);").fetchall()
    link_fks = conn.execute("PRAGMA foreign_key_list(name_subtitle_links);").fetchall()

    assert {(row[2], row[3], row[4]) for row in subtitle_fks} == {("titles", "title_id", "id")}
    assert {(row[2], row[3], row[4]) for row in link_fks} == {
        ("names", "name_id", "id"),
        ("subtitles", "subtitle_id", "id"),
    }


def test_active_name_uniqueness_is_enforced_by_partial_index() -> None:
    conn = sqlite3.connect(":memory:")
    apply_schema(conn)

    conn.execute(
        "INSERT INTO names(raw_name, normalized_name, deleted_at) VALUES (?, ?, ?);",
        ("Alice", "alice", None),
    )

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO names(raw_name, normalized_name, deleted_at) VALUES (?, ?, ?);",
            ("ALICE", "alice", None),
        )

    conn.execute(
        "INSERT INTO names(raw_name, normalized_name, deleted_at) VALUES (?, ?, ?);",
        ("ALICE", "alice", "2026-01-01T00:00:00Z"),
    )


def test_schema_and_migration_are_aligned() -> None:
    schema_sql = Path("db/schema.sql").read_text(encoding="utf-8")
    migration_sql = Path("db/migrations/0001_initial_schema.sql").read_text(encoding="utf-8")
    migration_sql += Path("db/migrations/0002_name_title_links.sql").read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS name_title_links" in schema_sql
    assert "CREATE TABLE IF NOT EXISTS name_title_links" in migration_sql

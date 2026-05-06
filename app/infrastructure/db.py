"""SQLite schema initialization helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from app.domain.public_id import new_public_id

DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "db" / "schema.sql"
_PUBLIC_ID_TABLES = (
    "names",
    "titles",
    "subtitles",
    "name_subtitle_links",
    "name_title_links",
    "change_logs",
)


def apply_schema(connection: sqlite3.Connection, schema_path: Path = DEFAULT_SCHEMA_PATH) -> None:
    """Apply schema SQL to an existing SQLite connection."""
    sql_script = schema_path.read_text(encoding="utf-8")
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.executescript(sql_script)
    ensure_public_ids(connection)


def initialize_database(
    db_path: Path, schema_path: Path = DEFAULT_SCHEMA_PATH
) -> sqlite3.Connection:
    """Create/open a SQLite database file and apply the bootstrap schema."""
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    apply_schema(connection=connection, schema_path=schema_path)
    return connection


def ensure_public_ids(connection: sqlite3.Connection) -> None:
    """Add and backfill nullable public_id columns for existing SQLite databases."""

    for table in _PUBLIC_ID_TABLES:
        _ensure_public_id_column(connection, table)
        connection.execute(
            f"CREATE UNIQUE INDEX IF NOT EXISTS uq_{table}_public_id "
            f"ON {table}(public_id) WHERE public_id IS NOT NULL"
        )
        rows = connection.execute(
            f"SELECT id FROM {table} WHERE public_id IS NULL ORDER BY id"
        ).fetchall()
        for row in rows:
            connection.execute(
                f"UPDATE {table} SET public_id = ? WHERE id = ?",
                (new_public_id(), int(row["id"])),
            )
    connection.commit()


def _ensure_public_id_column(connection: sqlite3.Connection, table: str) -> None:
    columns = {
        str(row["name"])
        for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
    }
    if "public_id" not in columns:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN public_id TEXT")

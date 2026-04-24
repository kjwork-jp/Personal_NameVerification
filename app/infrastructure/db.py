"""SQLite schema initialization helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path

DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "db" / "schema.sql"


def apply_schema(connection: sqlite3.Connection, schema_path: Path = DEFAULT_SCHEMA_PATH) -> None:
    """Apply schema SQL to an existing SQLite connection."""
    sql_script = schema_path.read_text(encoding="utf-8")
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.executescript(sql_script)


def initialize_database(
    db_path: Path, schema_path: Path = DEFAULT_SCHEMA_PATH
) -> sqlite3.Connection:
    """Create/open a SQLite database file and apply the bootstrap schema."""
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    apply_schema(connection=connection, schema_path=schema_path)
    return connection

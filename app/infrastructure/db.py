"""SQLite schema initialization helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from app.domain.normalization import normalize_with_raw
from app.domain.public_id import new_public_id

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = PROJECT_ROOT / "db" / "schema.sql"
DEFAULT_MIGRATIONS_DIR = PROJECT_ROOT / "migrations"
_SCHEMA_MIGRATIONS_DDL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""
_PUBLIC_ID_TABLES = (
    "names",
    "titles",
    "subtitles",
    "name_subtitle_links",
    "name_title_links",
    "change_logs",
)
_USER_AUTH_COLUMNS = {
    "auth_provider": "TEXT NOT NULL DEFAULT 'local'",
    "windows_account_name": "TEXT",
    "windows_sid": "TEXT",
}


def apply_schema(connection: sqlite3.Connection, schema_path: Path = DEFAULT_SCHEMA_PATH) -> None:
    """Apply schema SQL and pending migrations to an existing SQLite connection."""
    sql_script = schema_path.read_text(encoding="utf-8")
    connection.execute("PRAGMA foreign_keys = ON;")
    register_sqlite_functions(connection)
    ensure_legacy_public_id_columns(connection)
    connection.executescript(sql_script)
    apply_migrations(connection)
    ensure_user_auth_columns(connection)
    ensure_public_ids(connection)
    ensure_display_name_unique_indexes(connection)
    check_database_integrity(connection)


def register_sqlite_functions(connection: sqlite3.Connection) -> None:
    """Register app-specific SQLite functions required by expression indexes."""

    connection.create_function("app_normalize", 1, _sqlite_app_normalize, deterministic=True)


def apply_migrations(
    connection: sqlite3.Connection, migrations_dir: Path = DEFAULT_MIGRATIONS_DIR
) -> None:
    """Apply repo-managed SQLite migration files in filename order."""

    connection.executescript(_SCHEMA_MIGRATIONS_DDL)
    if not migrations_dir.exists():
        connection.commit()
        return

    applied_versions = {
        str(_row_value(row, "version", 0))
        for row in connection.execute("SELECT version FROM schema_migrations").fetchall()
    }
    migration_files = sorted(migrations_dir.glob("*.sql"))
    for migration_file in migration_files:
        version = migration_file.stem
        if version in applied_versions:
            continue
        connection.executescript(migration_file.read_text(encoding="utf-8"))
        connection.execute(
            "INSERT INTO schema_migrations (version) VALUES (?)",
            (version,),
        )
    connection.commit()


def initialize_database(
    db_path: Path, schema_path: Path = DEFAULT_SCHEMA_PATH
) -> sqlite3.Connection:
    """Create/open a SQLite database file and apply the bootstrap schema."""
    resolved_db_path = db_path.expanduser()
    if resolved_db_path.parent not in {Path(""), Path(".")}:
        resolved_db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(resolved_db_path)
    connection.row_factory = sqlite3.Row
    try:
        apply_schema(connection=connection, schema_path=schema_path)
    except Exception:
        connection.close()
        raise
    return connection


def check_database_integrity(connection: sqlite3.Connection) -> None:
    """Raise sqlite3.DatabaseError when SQLite integrity_check reports a problem."""

    rows = connection.execute("PRAGMA integrity_check;").fetchall()
    problems = [str(_row_value(row, "integrity_check", 0)) for row in rows]
    if problems == ["ok"]:
        return
    detail = "; ".join(problems) if problems else "no integrity_check result returned"
    raise sqlite3.DatabaseError(f"SQLite integrity check failed: {detail}")


def ensure_legacy_public_id_columns(connection: sqlite3.Connection) -> None:
    """Add public_id columns before schema indexes run against legacy tables."""

    for table in _PUBLIC_ID_TABLES:
        if _table_exists(connection, table):
            _ensure_public_id_column(connection, table)
    connection.commit()


def ensure_user_auth_columns(connection: sqlite3.Connection) -> None:
    """Add local/windows auth metadata columns for existing user databases."""

    if not _table_exists(connection, "users"):
        return
    columns = _table_columns(connection, "users")
    for column_name, ddl in _USER_AUTH_COLUMNS.items():
        if column_name not in columns:
            connection.execute(f"ALTER TABLE users ADD COLUMN {column_name} {ddl}")
    connection.execute("UPDATE users SET auth_provider = 'local' WHERE auth_provider IS NULL")
    connection.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_users_windows_sid
        ON users(windows_sid)
        WHERE windows_sid IS NOT NULL
        """)
    connection.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_users_windows_account_name
        ON users(windows_account_name)
        WHERE windows_account_name IS NOT NULL
        """)
    connection.commit()


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
                (new_public_id(), _row_value(row, "id", 0)),
            )
    connection.commit()


def ensure_display_name_unique_indexes(connection: sqlite3.Connection) -> None:
    """Create normalized active display-name unique indexes for titles/subtitles."""

    if not _table_exists(connection, "titles") or not _table_exists(connection, "subtitles"):
        return

    from app.application.duplicate_display_name_preflight import (
        inspect_duplicate_display_names,
    )

    report = inspect_duplicate_display_names(connection)
    if report.has_blockers:
        raise sqlite3.IntegrityError(_display_name_readiness_message(report))

    connection.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_titles_active_display_name
        ON titles(app_normalize(title_name))
        WHERE deleted_at IS NULL
        """)
    connection.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_subtitles_active_title_display_name
        ON subtitles(title_id, app_normalize(subtitle_name))
        WHERE deleted_at IS NULL
        """)
    connection.commit()


def _display_name_readiness_message(report: Any) -> str:
    entries = [
        "title/subtitle display-name index readiness failed",
        f"title_groups={len(report.title_duplicates)}",
        f"subtitle_groups={len(report.subtitle_duplicates)}",
    ]
    for group in report.title_duplicates:
        entries.append(
            "title_group("
            f"key={group.normalized_key!r}, "
            f"ids={group.ids!r}, "
            f"display_names={group.display_names!r})"
        )
    for group in report.subtitle_duplicates:
        entries.append(
            "subtitle_group("
            f"title_id={group.title_id!r}, "
            f"key={group.normalized_key!r}, "
            f"ids={group.ids!r}, "
            f"display_names={group.display_names!r})"
        )
    return "; ".join(entries)


def _sqlite_app_normalize(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    return normalize_with_raw(value).normalized_text


def _table_exists(connection: sqlite3.Connection, table: str) -> bool:
    row = connection.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table' AND name = ?
        """,
        (table,),
    ).fetchone()
    return row is not None


def _table_columns(connection: sqlite3.Connection, table: str) -> set[str]:
    return {
        str(_row_value(row, "name", 1))
        for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
    }


def _ensure_public_id_column(connection: sqlite3.Connection, table: str) -> None:
    columns = _table_columns(connection, table)
    if "public_id" not in columns:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN public_id TEXT")


def _row_value(row: Any, key: str, index: int) -> Any:
    try:
        return row[key]
    except (TypeError, IndexError):
        return row[index]

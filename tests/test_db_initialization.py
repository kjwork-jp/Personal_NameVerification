from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.infrastructure.db import check_database_integrity, initialize_database


def test_initialize_database_creates_parent_directories(tmp_path: Path) -> None:
    db_path = tmp_path / "nested" / "db" / "nameverification.db"

    connection = initialize_database(db_path)
    try:
        assert db_path.exists()
        assert db_path.parent.is_dir()
        assert connection.execute("PRAGMA integrity_check;").fetchone()[0] == "ok"
    finally:
        connection.close()


def test_initialize_database_applies_auth_migrations(tmp_path: Path) -> None:
    db_path = tmp_path / "nameverification.db"

    connection = initialize_database(db_path)
    try:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        assert "schema_migrations" in tables
        assert "users" in tables
        assert "app_settings" in tables
        assert "user_audit_logs" in tables
        assert (
            connection.execute(
                "SELECT 1 FROM schema_migrations WHERE version = ?",
                ("20260515_0001_auth_users_settings_audit",),
            ).fetchone()
            is not None
        )
    finally:
        connection.close()


def test_initialize_database_preserves_existing_data_when_migrating(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "existing.db"

    connection = initialize_database(db_path)
    try:
        connection.execute(
            "INSERT INTO names (raw_name, normalized_name, note) VALUES (?, ?, ?)",
            ("既存名", "既存名", "before migration reopen"),
        )
        connection.commit()
    finally:
        connection.close()

    reopened = initialize_database(db_path)
    try:
        assert reopened.execute("SELECT COUNT(*) FROM names").fetchone()[0] == 1
        assert reopened.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
        assert reopened.execute("PRAGMA integrity_check;").fetchone()[0] == "ok"
    finally:
        reopened.close()


def test_initialize_database_repairs_legacy_public_id_columns(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "legacy-public-id.db"
    legacy = sqlite3.connect(db_path)
    try:
        legacy.executescript(
            """
            CREATE TABLE names (
                id INTEGER PRIMARY KEY,
                raw_name TEXT NOT NULL,
                normalized_name TEXT NOT NULL,
                note TEXT,
                icon_path TEXT,
                deleted_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            INSERT INTO names(raw_name, normalized_name, note)
            VALUES ('Legacy Name', 'legacy name', 'before public_id migration');
            """
        )
        legacy.commit()
    finally:
        legacy.close()

    migrated = initialize_database(db_path)
    try:
        columns = {
            row[1] for row in migrated.execute("PRAGMA table_info(names)").fetchall()
        }
        assert "public_id" in columns
        row = migrated.execute(
            "SELECT raw_name, note, public_id FROM names WHERE id = 1"
        ).fetchone()
        assert row[0] == "Legacy Name"
        assert row[1] == "before public_id migration"
        assert isinstance(row[2], str)
        assert row[2]
        assert migrated.execute("PRAGMA integrity_check;").fetchone()[0] == "ok"
    finally:
        migrated.close()


def test_initialize_database_repairs_legacy_user_auth_columns(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "legacy-users.db"

    connection = initialize_database(db_path)
    try:
        connection.execute(
            """
            INSERT INTO users(
                operator_id,
                role,
                password_hash,
                password_salt,
                password_algorithm,
                password_iterations,
                password_updated_at
            ) VALUES (?, 'admin', 'hash', 'salt', 'pbkdf2_sha256', 1000, CURRENT_TIMESTAMP)
            """,
            ("legacy-admin",),
        )
        connection.execute("ALTER TABLE users RENAME TO users_with_auth_columns")
        connection.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                public_id TEXT,
                operator_id TEXT NOT NULL UNIQUE,
                display_name TEXT,
                role TEXT NOT NULL CHECK(role IN ('viewer', 'editor', 'admin')),
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                password_algorithm TEXT NOT NULL DEFAULT 'pbkdf2_sha256',
                password_iterations INTEGER NOT NULL,
                password_updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                disabled_at TEXT,
                failed_login_count INTEGER NOT NULL DEFAULT 0,
                locked_until TEXT,
                last_login_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            INSERT INTO users(
                id,
                public_id,
                operator_id,
                display_name,
                role,
                password_hash,
                password_salt,
                password_algorithm,
                password_iterations,
                password_updated_at,
                disabled_at,
                failed_login_count,
                locked_until,
                last_login_at,
                created_at,
                updated_at
            )
            SELECT
                id,
                public_id,
                operator_id,
                display_name,
                role,
                password_hash,
                password_salt,
                password_algorithm,
                password_iterations,
                password_updated_at,
                disabled_at,
                failed_login_count,
                locked_until,
                last_login_at,
                created_at,
                updated_at
            FROM users_with_auth_columns
            """
        )
        connection.execute("DROP TABLE users_with_auth_columns")
        connection.commit()
    finally:
        connection.close()

    migrated = initialize_database(db_path)
    try:
        columns = {
            row[1] for row in migrated.execute("PRAGMA table_info(users)").fetchall()
        }
        assert {"auth_provider", "windows_account_name", "windows_sid"} <= columns
        row = migrated.execute(
            """
            SELECT operator_id, auth_provider, windows_account_name, windows_sid
            FROM users
            WHERE operator_id = 'legacy-admin'
            """
        ).fetchone()
        assert tuple(row) == ("legacy-admin", "local", None, None)
        assert migrated.execute("PRAGMA integrity_check;").fetchone()[0] == "ok"
    finally:
        migrated.close()


def test_check_database_integrity_accepts_ok_result() -> None:
    connection = sqlite3.connect(":memory:")
    try:
        check_database_integrity(connection)
    finally:
        connection.close()


class _FakeIntegrityConnection:
    def __init__(self, rows: list[tuple[str]]) -> None:
        self.rows = rows

    def execute(self, sql: str) -> _FakeIntegrityConnection:
        assert sql == "PRAGMA integrity_check;"
        return self

    def fetchall(self) -> list[tuple[str]]:
        return self.rows


def test_check_database_integrity_raises_on_problem() -> None:
    connection = _FakeIntegrityConnection([("row 1 missing from index sample",)])

    with pytest.raises(sqlite3.DatabaseError, match="row 1 missing"):
        check_database_integrity(connection)  # type: ignore[arg-type]

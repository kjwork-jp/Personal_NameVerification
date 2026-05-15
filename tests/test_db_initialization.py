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

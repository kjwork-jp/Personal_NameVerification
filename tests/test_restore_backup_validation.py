"""Tests for backup restore file validation."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.domain.errors import ValidationError
from app.infrastructure.db import initialize_database
from app.infrastructure.restore_backup import restore_database_from_backup


def test_restore_database_from_valid_backup(tmp_path: Path) -> None:
    backup_path = tmp_path / "backup.db"
    target_path = tmp_path / "target.db"
    source_connection = initialize_database(backup_path)
    source_connection.execute(
        "INSERT INTO names(raw_name, normalized_name, created_at, updated_at) VALUES (?, ?, ?, ?)",
        ("Alice", "alice", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"),
    )
    source_connection.commit()
    source_connection.close()

    restored = restore_database_from_backup(backup_path, target_path)

    assert restored == target_path
    target_connection = sqlite3.connect(target_path)
    try:
        assert target_connection.execute("SELECT raw_name FROM names").fetchone()[0] == "Alice"
    finally:
        target_connection.close()


def test_restore_rejects_invalid_sqlite_backup(tmp_path: Path) -> None:
    backup_path = tmp_path / "not_sqlite.db"
    target_path = tmp_path / "target.db"
    backup_path.write_text("not a sqlite database", encoding="utf-8")

    with pytest.raises(ValidationError, match="not a valid sqlite database"):
        restore_database_from_backup(backup_path, target_path)

    assert not target_path.exists()


def test_restore_rejects_same_source_and_target(tmp_path: Path) -> None:
    db_path = tmp_path / "same.db"
    connection = initialize_database(db_path)
    connection.close()

    with pytest.raises(ValidationError, match="must be different files"):
        restore_database_from_backup(db_path, db_path)

"""Tests for backup-restore foundation service."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.application.backup_restore_services import BackupRestoreService
from app.application.core_services import CoreService, NameInput
from app.domain.errors import AuthorizationError, ValidationError
from app.infrastructure.db import initialize_database


def _seed_name(db_path: Path, raw_name: str) -> None:
    conn = initialize_database(db_path)
    conn.row_factory = sqlite3.Row
    core = CoreService(conn)
    core.create_name(NameInput(raw_name=raw_name), operator_id="op-1")
    conn.commit()
    conn.close()


def _read_names(db_path: Path) -> list[str]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT raw_name FROM names ORDER BY id").fetchall()
    conn.close()
    return [str(row["raw_name"]) for row in rows]


def test_restore_success_for_admin(tmp_path: Path) -> None:
    backup_db = tmp_path / "backup.sqlite3"
    target_db = tmp_path / "target.sqlite3"
    _seed_name(backup_db, "FromBackup")
    _seed_name(target_db, "OriginalTarget")

    service = BackupRestoreService()
    result = service.restore_database(backup_path=backup_db, target_db_path=target_db, role="admin")

    assert result == target_db.resolve()
    assert _read_names(target_db) == ["FromBackup"]


def test_restore_rejects_viewer_and_editor(tmp_path: Path) -> None:
    backup_db = tmp_path / "backup.sqlite3"
    target_db = tmp_path / "target.sqlite3"
    _seed_name(backup_db, "FromBackup")
    _seed_name(target_db, "OriginalTarget")

    service = BackupRestoreService()

    with pytest.raises(AuthorizationError):
        service.restore_database(backup_path=backup_db, target_db_path=target_db, role="viewer")

    with pytest.raises(AuthorizationError):
        service.restore_database(backup_path=backup_db, target_db_path=target_db, role="editor")


def test_restore_path_validation(tmp_path: Path) -> None:
    backup_db = tmp_path / "backup.sqlite3"
    target_db = tmp_path / "target.sqlite3"
    _seed_name(backup_db, "FromBackup")
    _seed_name(target_db, "OriginalTarget")

    service = BackupRestoreService()

    with pytest.raises(ValidationError):
        service.restore_database(
            backup_path=tmp_path / "missing.sqlite3",
            target_db_path=target_db,
            role="admin",
        )

    backup_dir = tmp_path / "backup_dir"
    backup_dir.mkdir()
    with pytest.raises(ValidationError):
        service.restore_database(backup_path=backup_dir, target_db_path=target_db, role="admin")

    with pytest.raises(ValidationError):
        service.restore_database(backup_path=backup_db, target_db_path=backup_db, role="admin")

    with pytest.raises(ValidationError):
        service.restore_database(
            backup_path=backup_db,
            target_db_path=(tmp_path / "missing_parent" / "target.sqlite3"),
            role="admin",
        )

"""Application service for backup-restore operations."""

from __future__ import annotations

from pathlib import Path

from app.application.authorization import ServiceRole, require_admin
from app.infrastructure.restore_backup import restore_database_from_backup


class BackupRestoreService:
    """Service entrypoint for restoring DB files from backup artifacts.

    Notes:
        Active SQLite connections to the target DB should be closed by caller before restore.
    """

    def restore_database(
        self,
        backup_path: Path,
        target_db_path: Path,
        role: ServiceRole = "admin",
    ) -> Path:
        require_admin(role, action="restore_database")
        return restore_database_from_backup(backup_path=backup_path, target_db_path=target_db_path)

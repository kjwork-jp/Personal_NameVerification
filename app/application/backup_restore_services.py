"""Application service for backup-restore operations."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

from app.application.authorization import ServiceRole, require_admin
from app.application.runtime_paths import resolve_destructive_backup_dir
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
    ) -> tuple[Path, Path]:
        require_admin(role, action="restore_database")
        before_restore_backup = self.create_before_restore_backup(target_db_path)
        restored = restore_database_from_backup(
            backup_path=backup_path, target_db_path=target_db_path
        )
        return restored, before_restore_backup

    def create_before_restore_backup(self, target_db_path: Path) -> Path:
        source = target_db_path.expanduser().resolve()
        backup_dir = resolve_destructive_backup_dir(source, operation="before_restore")
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"before_restore_{stamp}.db"
        shutil.copy2(source, backup_path)
        return backup_path

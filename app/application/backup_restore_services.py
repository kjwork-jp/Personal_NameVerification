"""Application service for backup-restore operations."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

from app.application.authorization import ServiceRole, require_admin
from app.application.runtime_paths import resolve_destructive_backup_dir
from app.domain.errors import ValidationError
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
        source = backup_path.expanduser().resolve()
        target = target_db_path.expanduser().resolve()
        self._validate_restore_paths(source, target)
        before_restore_backup = self.create_before_restore_backup(target)
        restored = restore_database_from_backup(
            backup_path=source, target_db_path=target
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

    def _validate_restore_paths(self, backup_path: Path, target_db_path: Path) -> None:
        if not backup_path.exists():
            raise ValidationError(f"backup source does not exist: {backup_path}")
        if not backup_path.is_file():
            raise ValidationError(f"backup source is not a file: {backup_path}")
        if backup_path == target_db_path:
            raise ValidationError("backup source and restore target must be different files")
        parent = target_db_path.parent
        if not parent.exists() or not parent.is_dir():
            raise ValidationError(f"target database directory does not exist: {parent}")
        if target_db_path.exists() and target_db_path.is_dir():
            raise ValidationError(f"target database path points to a directory: {target_db_path}")

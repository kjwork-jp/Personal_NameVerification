"""Application service for backup-restore operations."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

from app.application.authorization import ServiceRole, require_admin
from app.application.runtime_paths import resolve_destructive_backup_dir
from app.domain.errors import ValidationError
from app.infrastructure.restore_backup import restore_database_from_backup


class RestoreResult(tuple[Path, Path]):
    """Tuple-like restore result with legacy Path equality compatibility."""

    restored_path: Path
    before_restore_path: Path

    def __new__(cls, restored_path: Path, before_restore_path: Path) -> RestoreResult:
        value = tuple.__new__(cls, (restored_path, before_restore_path))
        value.restored_path = restored_path
        value.before_restore_path = before_restore_path
        return value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Path):
            return self.restored_path == other
        return tuple.__eq__(self, other)

    def __hash__(self) -> int:
        return tuple.__hash__(self)


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
        source, target = self._validate_restore_inputs(backup_path, target_db_path)
        before_restore_backup = self.create_before_restore_backup(target)
        restored = restore_database_from_backup(backup_path=source, target_db_path=target)
        return RestoreResult(restored, before_restore_backup)

    def create_before_restore_backup(self, target_db_path: Path) -> Path:
        source = target_db_path.expanduser().resolve()
        if not source.exists() or not source.is_file():
            raise ValidationError(f"restore target database does not exist: {source}")
        backup_dir = resolve_destructive_backup_dir(source, operation="before_restore")
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"before_restore_{stamp}.db"
        shutil.copy2(source, backup_path)
        return backup_path

    def _validate_restore_inputs(
        self, backup_path: Path, target_db_path: Path
    ) -> tuple[Path, Path]:
        source = backup_path.expanduser().resolve()
        target = target_db_path.expanduser().resolve()

        if not source.exists():
            raise ValidationError(f"backup source does not exist: {source}")
        if not source.is_file():
            raise ValidationError(f"backup source is not a file: {source}")
        if source == target:
            raise ValidationError("backup source and restore target must be different files")

        parent = target.parent
        if not parent.exists() or not parent.is_dir():
            raise ValidationError(f"target database directory does not exist: {parent}")
        if not target.exists():
            raise ValidationError(f"restore target database does not exist: {target}")
        if not target.is_file():
            raise ValidationError(f"target database path points to a directory: {target}")
        return source, target

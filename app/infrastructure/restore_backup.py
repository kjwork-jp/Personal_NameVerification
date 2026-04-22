"""Backup restore helper for SQLite database files."""

from __future__ import annotations

import shutil
from pathlib import Path

from app.domain.errors import ValidationError


def restore_database_from_backup(backup_path: Path, target_db_path: Path) -> Path:
    """Restore SQLite DB by replacing target file with backup file contents.

    Notes:
        - Caller should close active DB connections before invoking this helper.
        - This helper performs file-level replacement only; schema migration is out of scope.
    """
    source = backup_path.resolve()
    target = target_db_path.resolve()

    if not source.exists():
        raise ValidationError(f"backup source does not exist: {source}")
    if not source.is_file():
        raise ValidationError(f"backup source is not a file: {source}")

    if source == target:
        raise ValidationError("backup source and restore target must be different files")

    parent = target.parent
    if not parent.exists() or not parent.is_dir():
        raise ValidationError(f"target database directory does not exist: {parent}")

    if target.exists() and target.is_dir():
        raise ValidationError(f"target database path points to a directory: {target}")

    temp_target = target.with_suffix(f"{target.suffix}.restore_tmp")
    try:
        shutil.copy2(source, temp_target)
        temp_target.replace(target)
    finally:
        if temp_target.exists():
            temp_target.unlink()

    return target

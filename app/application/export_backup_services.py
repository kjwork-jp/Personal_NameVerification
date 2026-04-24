"""Application services for export and backup-create operations."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from app.application.authorization import ServiceRole, require_editor_or_admin
from app.infrastructure.export_backup import (
    create_backup_file,
    export_sql_dump,
    export_tables_to_csv,
    export_tables_to_json,
)


class ExportBackupService:
    """Service entrypoint for file export and DB backup-create workflows."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute("PRAGMA foreign_keys = ON;")

    def export_csv(self, output_dir: Path, role: ServiceRole = "admin") -> dict[str, Path]:
        require_editor_or_admin(role, action="export_csv")
        return export_tables_to_csv(self._connection, output_dir)

    def export_json(self, output_path: Path, role: ServiceRole = "admin") -> Path:
        require_editor_or_admin(role, action="export_json")
        return export_tables_to_json(self._connection, output_path)

    def export_sql_dump(self, output_path: Path, role: ServiceRole = "admin") -> Path:
        require_editor_or_admin(role, action="export_sql_dump")
        return export_sql_dump(self._connection, output_path)

    def create_backup(self, db_path: Path, backup_path: Path, role: ServiceRole = "admin") -> Path:
        require_editor_or_admin(role, action="create_backup")
        return create_backup_file(db_path=db_path, backup_path=backup_path)

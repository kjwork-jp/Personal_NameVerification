"""Application services for export and backup-create operations."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.application.authorization import ServiceRole, require_editor_or_admin
from app.infrastructure.export_backup import (
    create_backup_file,
    export_sanitized_tables_to_json,
    export_sql_dump,
    export_tables_to_csv,
    export_tables_to_json,
)


class ExportBackupService:
    """Service entrypoint for file export and DB backup-create workflows.

    The desktop UI runs export/backup actions on a worker thread. A SQLite
    connection created on the main UI thread cannot be used from that worker
    thread, so production usage should pass ``database_path``. When supplied,
    each export operation opens and closes its own thread-local connection.

    The ``connection`` fallback is kept for tests and direct synchronous calls.
    """

    def __init__(
        self,
        connection: sqlite3.Connection,
        *,
        database_path: Path | None = None,
    ) -> None:
        self._connection = connection
        self._database_path = database_path
        self._connection.execute("PRAGMA foreign_keys = ON;")

    def export_csv(self, output_dir: Path, role: ServiceRole = "admin") -> dict[str, Path]:
        require_editor_or_admin(role, action="export_csv")
        with self._operation_connection() as connection:
            return export_tables_to_csv(connection, output_dir)

    def export_json(self, output_path: Path, role: ServiceRole = "admin") -> Path:
        require_editor_or_admin(role, action="export_json")
        with self._operation_connection() as connection:
            return export_tables_to_json(connection, output_path)

    def export_sanitized_json(self, output_path: Path, role: ServiceRole = "admin") -> Path:
        require_editor_or_admin(role, action="export_sanitized_json")
        with self._operation_connection() as connection:
            return export_sanitized_tables_to_json(connection, output_path)

    def export_sql_dump(self, output_path: Path, role: ServiceRole = "admin") -> Path:
        require_editor_or_admin(role, action="export_sql_dump")
        with self._operation_connection() as connection:
            return export_sql_dump(connection, output_path)

    def create_backup(self, db_path: Path, backup_path: Path, role: ServiceRole = "admin") -> Path:
        require_editor_or_admin(role, action="create_backup")
        return create_backup_file(db_path=db_path, backup_path=backup_path)

    @contextmanager
    def _operation_connection(self) -> Iterator[sqlite3.Connection]:
        if self._database_path is None:
            yield self._connection
            return

        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON;")
        try:
            yield connection
        finally:
            connection.close()

"""Application service for CSV/JSON import foundation."""

from __future__ import annotations

import shutil
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from app.application.authorization import ServiceRole, require_admin
from app.application.runtime_paths import resolve_destructive_backup_dir
from app.infrastructure.import_data import (
    IMPORT_TABLES,
    import_from_csv_directory,
    import_from_json_file,
    read_table_counts,
)


class ImportService:
    """Import data into an empty SQLite DB from CSV/JSON exports."""

    def __init__(
        self,
        connection: sqlite3.Connection,
        *,
        database_path: Path | None = None,
    ) -> None:
        self._connection = connection
        self._database_path = database_path
        self._connection.execute("PRAGMA foreign_keys = ON;")

    def import_csv(self, csv_dir: Path, role: ServiceRole = "admin") -> tuple[dict[str, int], Path]:
        require_admin(role, action="import_csv")
        before_import_backup = self.create_before_import_backup()
        with self._operation_connection() as connection:
            return import_from_csv_directory(connection, csv_dir), before_import_backup

    def import_json(
        self, json_path: Path, role: ServiceRole = "admin"
    ) -> tuple[dict[str, int], Path]:
        require_admin(role, action="import_json")
        before_import_backup = self.create_before_import_backup()
        with self._operation_connection() as connection:
            return import_from_json_file(connection, json_path), before_import_backup

    def preview_import_target_state(self) -> dict[str, int]:
        with self._operation_connection() as connection:
            return read_table_counts(connection, IMPORT_TABLES)

    def create_before_import_backup(self) -> Path:
        if self._database_path is None:
            raise ValueError("database_path is required for pre-import backup")
        source = self._database_path.expanduser().resolve()
        backup_dir = resolve_destructive_backup_dir(source, operation="before_import")
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"before_import_{stamp}.db"
        shutil.copy2(source, backup_path)
        return backup_path

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

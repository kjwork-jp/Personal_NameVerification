"""Application service for CSV/JSON import foundation."""

from __future__ import annotations

import json
import shutil
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from app.application.authorization import ServiceRole, require_admin
from app.application.runtime_paths import resolve_destructive_backup_dir
from app.domain.errors import ValidationError
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
        self._preflight_import_csv(csv_dir)
        before_import_backup = self.create_before_import_backup()
        with self._operation_connection() as connection:
            return import_from_csv_directory(connection, csv_dir), before_import_backup

    def import_json(
        self, json_path: Path, role: ServiceRole = "admin"
    ) -> tuple[dict[str, int], Path]:
        require_admin(role, action="import_json")
        self._preflight_import_json(json_path)
        before_import_backup = self.create_before_import_backup()
        with self._operation_connection() as connection:
            return import_from_json_file(connection, json_path), before_import_backup

    def preview_import_target_state(self) -> dict[str, int]:
        with self._operation_connection() as connection:
            return read_table_counts(connection, IMPORT_TABLES)

    def create_before_import_backup(self) -> Path:
        source = self._resolve_database_path()
        backup_dir = resolve_destructive_backup_dir(source, operation="before_import")
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"before_import_{stamp}.db"
        shutil.copy2(source, backup_path)
        return backup_path

    def _resolve_database_path(self) -> Path:
        if self._database_path is not None:
            return self._database_path.expanduser().resolve()
        row = self._connection.execute("PRAGMA database_list").fetchall()
        for item in row:
            name = str(item[1]) if len(item) > 1 else ""
            file_path = str(item[2]) if len(item) > 2 else ""
            if name == "main" and file_path:
                return Path(file_path).expanduser().resolve()
        raise ValidationError(
            "対象DBのファイルパスを特定できません。ファイルDBを使用してください。"
        )

    def _ensure_empty_target(self) -> None:
        counts = self.preview_import_target_state()
        for table_name, count in counts.items():
            if count > 0:
                raise ValidationError(
                    f"import target db must be empty: table {table_name} has {count} rows"
                )

    def _preflight_import_csv(self, csv_dir: Path) -> None:
        self._ensure_empty_target()
        source_dir = csv_dir.resolve()
        if not source_dir.exists() or not source_dir.is_dir():
            raise ValidationError(f"csv directory does not exist: {source_dir}")
        for table_name in IMPORT_TABLES:
            file_path = source_dir / f"{table_name}.csv"
            if not file_path.exists() or not file_path.is_file():
                raise ValidationError(f"required csv file is missing: {file_path}")

    def _preflight_import_json(self, json_path: Path) -> None:
        self._ensure_empty_target()
        source = json_path.resolve()
        if not source.exists() or not source.is_file():
            raise ValidationError(f"json file does not exist: {source}")
        try:
            json.loads(source.read_text("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValidationError("json file is invalid") from exc

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

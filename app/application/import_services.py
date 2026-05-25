"""Application service for CSV/JSON import foundation."""

from __future__ import annotations

import csv
import json
import shutil
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.application.authorization import ServiceRole, require_admin
from app.application.runtime_paths import resolve_destructive_backup_dir
from app.domain.errors import ValidationError
from app.infrastructure.import_data import (
    IMPORT_TABLES,
    import_from_csv_directory,
    import_from_json_file,
    read_table_counts,
)


@dataclass(frozen=True)
class ImportSourcePreview:
    """Non-destructive import source diagnostics."""

    source_type: str
    source_path: str
    table_counts: dict[str, int]
    missing_tables: tuple[str, ...]
    invalid_tables: tuple[str, ...]
    unknown_tables: tuple[str, ...]
    ready: bool


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
        self._validate_csv_source(csv_dir)
        with self._operation_connection() as connection:
            self._validate_empty_target(connection)
        before_import_backup = self.create_before_import_backup()
        with self._operation_connection() as connection:
            return import_from_csv_directory(connection, csv_dir), before_import_backup

    def import_json(
        self, json_path: Path, role: ServiceRole = "admin"
    ) -> tuple[dict[str, int], Path]:
        require_admin(role, action="import_json")
        self._validate_json_source(json_path)
        with self._operation_connection() as connection:
            self._validate_empty_target(connection)
        before_import_backup = self.create_before_import_backup()
        with self._operation_connection() as connection:
            return import_from_json_file(connection, json_path), before_import_backup

    def preview_import_target_state(self) -> dict[str, int]:
        with self._operation_connection() as connection:
            return read_table_counts(connection, IMPORT_TABLES)

    def preview_csv_source(self, csv_dir: Path) -> ImportSourcePreview:
        """Preview CSV source counts and structural readiness without importing."""

        target_dir = csv_dir.expanduser().resolve()
        if not target_dir.exists() or not target_dir.is_dir():
            raise ValidationError(f"csv directory does not exist: {target_dir}")

        table_counts: dict[str, int] = {}
        missing_tables: list[str] = []
        invalid_tables: list[str] = []
        expected_files = {f"{table_name}.csv" for table_name in IMPORT_TABLES}
        actual_files = {path.name for path in target_dir.glob("*.csv") if path.is_file()}
        unknown_tables = tuple(
            sorted(path_name.removesuffix(".csv") for path_name in actual_files - expected_files)
        )

        for table_name in IMPORT_TABLES:
            file_path = target_dir / f"{table_name}.csv"
            if not file_path.exists() or not file_path.is_file():
                missing_tables.append(table_name)
                continue
            try:
                with file_path.open("r", encoding="utf-8", newline="") as fp:
                    reader = csv.DictReader(fp)
                    if reader.fieldnames is None:
                        invalid_tables.append(table_name)
                        table_counts[table_name] = 0
                        continue
                    table_counts[table_name] = sum(1 for _ in reader)
            except csv.Error:
                invalid_tables.append(table_name)
                table_counts[table_name] = 0

        ready = not missing_tables and not invalid_tables
        return ImportSourcePreview(
            source_type="csv",
            source_path=str(target_dir),
            table_counts=table_counts,
            missing_tables=tuple(missing_tables),
            invalid_tables=tuple(invalid_tables),
            unknown_tables=unknown_tables,
            ready=ready,
        )

    def preview_json_source(self, json_path: Path) -> ImportSourcePreview:
        """Preview JSON source counts and structural readiness without importing."""

        source = json_path.expanduser().resolve()
        if not source.exists() or not source.is_file():
            raise ValidationError(f"json file does not exist: {source}")
        try:
            payload = json.loads(source.read_text("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValidationError("json file is invalid") from exc
        if not isinstance(payload, dict):
            raise ValidationError("json payload must be an object")

        table_counts: dict[str, int] = {}
        missing_tables: list[str] = []
        invalid_tables: list[str] = []
        expected_tables = set(IMPORT_TABLES)
        unknown_tables = tuple(sorted(str(key) for key in payload.keys() - expected_tables))

        for table_name in IMPORT_TABLES:
            if table_name not in payload:
                missing_tables.append(table_name)
                continue
            rows = payload[table_name]
            if not isinstance(rows, list):
                invalid_tables.append(table_name)
                table_counts[table_name] = 0
                continue
            if any(not isinstance(row, dict) for row in rows):
                invalid_tables.append(table_name)
            table_counts[table_name] = len(rows)

        ready = not missing_tables and not invalid_tables
        return ImportSourcePreview(
            source_type="json",
            source_path=str(source),
            table_counts=table_counts,
            missing_tables=tuple(missing_tables),
            invalid_tables=tuple(invalid_tables),
            unknown_tables=unknown_tables,
            ready=ready,
        )

    def create_before_import_backup(self) -> Path:
        source = self._resolve_database_path()
        if not source.exists() or not source.is_file():
            raise ValidationError(f"import target database does not exist: {source}")
        backup_dir = resolve_destructive_backup_dir(source, operation="before_import")
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"before_import_{stamp}.db"
        shutil.copy2(source, backup_path)
        return backup_path

    def _resolve_database_path(self) -> Path:
        if self._database_path is not None:
            return self._database_path.expanduser().resolve()

        rows = self._connection.execute("PRAGMA database_list").fetchall()
        for candidate in rows:
            name = str(candidate[1])
            file_name = str(candidate[2] or "")
            if name == "main" and file_name.strip():
                return Path(file_name).expanduser().resolve()
        raise ValidationError("file-backed main database is required for pre-import backup")

    def _validate_empty_target(self, connection: sqlite3.Connection) -> None:
        for table_name, count in read_table_counts(connection, IMPORT_TABLES).items():
            if count > 0:
                raise ValidationError(
                    f"import target db must be empty: table {table_name} has {count} rows"
                )

    def _validate_csv_source(self, csv_dir: Path) -> None:
        target_dir = csv_dir.expanduser().resolve()
        if not target_dir.exists() or not target_dir.is_dir():
            raise ValidationError(f"csv directory does not exist: {target_dir}")
        for table_name in IMPORT_TABLES:
            file_path = target_dir / f"{table_name}.csv"
            if not file_path.exists() or not file_path.is_file():
                raise ValidationError(f"required csv file is missing: {file_path}")
            try:
                with file_path.open("r", encoding="utf-8", newline="") as fp:
                    _ = csv.DictReader(fp).fieldnames
            except csv.Error as exc:
                raise ValidationError(f"csv file is invalid: {file_path}") from exc

    def _validate_json_source(self, json_path: Path) -> None:
        source = json_path.expanduser().resolve()
        if not source.exists() or not source.is_file():
            raise ValidationError(f"json file does not exist: {source}")
        try:
            payload = json.loads(source.read_text("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValidationError("json file is invalid") from exc
        if not isinstance(payload, dict):
            raise ValidationError("json payload must be an object")
        for table_name in IMPORT_TABLES:
            if table_name not in payload:
                raise ValidationError(f"json payload missing required key: {table_name}")
            if not isinstance(payload[table_name], list):
                raise ValidationError(f"json payload key is not a list: {table_name}")

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

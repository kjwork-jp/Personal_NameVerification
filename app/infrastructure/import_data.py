"""CSV/JSON import helpers for empty SQLite databases."""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path
from typing import Any

from app.domain.errors import ValidationError

IMPORT_TABLES: tuple[str, ...] = (
    "names",
    "titles",
    "subtitles",
    "name_subtitle_links",
    "change_logs",
)

_IMPORT_ORDER: tuple[str, ...] = (
    "titles",
    "names",
    "subtitles",
    "name_subtitle_links",
    "change_logs",
)


def import_from_csv_directory(
    connection: sqlite3.Connection,
    csv_dir: Path,
    *,
    table_names: tuple[str, ...] = IMPORT_TABLES,
) -> dict[str, int]:
    """Import CSV files into an empty SQLite DB.

    Expects one file per table: `<table_name>.csv`.
    """
    target_dir = csv_dir.resolve()
    if not target_dir.exists() or not target_dir.is_dir():
        raise ValidationError(f"csv directory does not exist: {target_dir}")

    _validate_empty_target_db(connection, table_names)

    files: dict[str, Path] = {}
    for table_name in table_names:
        file_path = target_dir / f"{table_name}.csv"
        if not file_path.exists() or not file_path.is_file():
            raise ValidationError(f"required csv file is missing: {file_path}")
        files[table_name] = file_path

    imported_counts: dict[str, int] = {}
    with connection:
        for table_name in _IMPORT_ORDER:
            if table_name not in table_names:
                continue

            columns, nullable_columns = _table_columns(connection, table_name)
            with files[table_name].open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                header = reader.fieldnames or []
                _validate_required_columns(table_name, list(header), columns)
                rows = [
                    _normalize_row_values(dict(row), columns, nullable_columns) for row in reader
                ]
            _insert_rows(connection, table_name, columns, rows)
            imported_counts[table_name] = len(rows)

    return imported_counts


def import_from_json_file(
    connection: sqlite3.Connection,
    json_path: Path,
    *,
    table_names: tuple[str, ...] = IMPORT_TABLES,
) -> dict[str, int]:
    """Import JSON export payload into an empty SQLite DB."""
    source = json_path.resolve()
    if not source.exists() or not source.is_file():
        raise ValidationError(f"json file does not exist: {source}")

    _validate_empty_target_db(connection, table_names)

    try:
        payload = json.loads(source.read_text("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError("json file is invalid") from exc

    if not isinstance(payload, dict):
        raise ValidationError("json payload must be an object")

    for table_name in table_names:
        if table_name not in payload:
            raise ValidationError(f"json payload missing required key: {table_name}")
        if not isinstance(payload[table_name], list):
            raise ValidationError(f"json payload key is not a list: {table_name}")

    imported_counts: dict[str, int] = {}
    with connection:
        for table_name in _IMPORT_ORDER:
            if table_name not in table_names:
                continue

            columns, _ = _table_columns(connection, table_name)
            rows_raw = payload[table_name]
            rows: list[dict[str, Any]] = []
            for row in rows_raw:
                if not isinstance(row, dict):
                    raise ValidationError(f"json row is not object: {table_name}")
                _validate_required_columns(table_name, list(row.keys()), columns)
                rows.append({key: row.get(key) for key in columns})

            _insert_rows(connection, table_name, columns, rows)
            imported_counts[table_name] = len(rows)

    return imported_counts


def _validate_empty_target_db(connection: sqlite3.Connection, table_names: tuple[str, ...]) -> None:
    for table_name in table_names:
        count_row = connection.execute(f"SELECT COUNT(1) AS c FROM {table_name}").fetchone()
        count = int(count_row[0]) if count_row is not None else 0
        if count > 0:
            raise ValidationError(
                f"import target db must be empty: table {table_name} has {count} rows"
            )


def _table_columns(connection: sqlite3.Connection, table_name: str) -> tuple[list[str], set[str]]:
    pragma_rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    columns = [str(row[1]) for row in pragma_rows]
    nullable = {str(row[1]) for row in pragma_rows if int(row[3]) == 0}
    return columns, nullable


def _validate_required_columns(table_name: str, provided: list[str], expected: list[str]) -> None:
    missing = [col for col in expected if col not in provided]
    if missing:
        raise ValidationError(f"{table_name} is missing required columns: {missing}")


def _normalize_row_values(
    row: dict[str, str],
    columns: list[str],
    nullable_columns: set[str],
) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for column in columns:
        value = row.get(column)
        if value == "" and column in nullable_columns:
            normalized[column] = None
        else:
            normalized[column] = value
    return normalized


def _insert_rows(
    connection: sqlite3.Connection,
    table_name: str,
    columns: list[str],
    rows: list[dict[str, Any]],
) -> None:
    if not rows:
        return

    placeholders = ", ".join(["?"] * len(columns))
    columns_sql = ", ".join(columns)
    sql = f"INSERT INTO {table_name} ({columns_sql}) VALUES ({placeholders})"
    values = [tuple(row[column] for column in columns) for row in rows]
    connection.executemany(sql, values)

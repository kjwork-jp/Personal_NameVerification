"""File export/backup helpers for SQLite-backed data."""

from __future__ import annotations

import csv
import json
import sqlite3
from os import PathLike
from pathlib import Path

from app.domain.errors import ValidationError

EXPORT_TABLES: tuple[str, ...] = (
    "names",
    "titles",
    "subtitles",
    "name_subtitle_links",
    "name_title_links",
    "change_logs",
)

SANITIZED_EXPORT_TABLES: tuple[str, ...] = (
    "names",
    "titles",
    "subtitles",
    "name_subtitle_links",
    "name_title_links",
)


def export_tables_to_csv(
    connection: sqlite3.Connection,
    output_dir: Path | PathLike[str],
    *,
    table_names: tuple[str, ...] = EXPORT_TABLES,
) -> dict[str, Path]:
    """Export each table into a dedicated CSV file under output_dir."""
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    if not output_dir.is_dir():
        raise ValidationError(f"output path is not a directory: {output_dir}")

    exported: dict[str, Path] = {}
    for table_name in table_names:
        rows = connection.execute(f"SELECT * FROM {table_name}").fetchall()
        output_path = output_dir / f"{table_name}.csv"

        with output_path.open("w", encoding="utf-8", newline="") as csv_file:
            if rows:
                field_names = list(rows[0].keys())
                writer = csv.DictWriter(csv_file, fieldnames=field_names)
                writer.writeheader()
                for row in rows:
                    writer.writerow(dict(row))
            else:
                columns = _column_names(connection, table_name)
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(columns)

        exported[table_name] = output_path

    return exported


def export_tables_to_json(
    connection: sqlite3.Connection,
    output_path: Path | PathLike[str],
    *,
    table_names: tuple[str, ...] = EXPORT_TABLES,
) -> Path:
    """Export target tables to a single JSON file."""
    validated = _validated_output_file_path(output_path)
    payload: dict[str, list[dict[str, object]]] = {}
    for table_name in table_names:
        rows = connection.execute(f"SELECT * FROM {table_name}").fetchall()
        payload[table_name] = [dict(row) for row in rows]

    validated.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), "utf-8")
    return validated


def export_sanitized_tables_to_json(
    connection: sqlite3.Connection,
    output_path: Path | PathLike[str],
) -> Path:
    """Export shareable application data without audit/auth/admin tables.

    This intentionally uses an allowlist of application data tables instead of a
    full database dump. Authentication/admin tables and operation/audit evidence
    such as users, settings, schema metadata, user audit logs, and change_logs
    are not exported.
    """

    return export_tables_to_json(
        connection,
        output_path,
        table_names=SANITIZED_EXPORT_TABLES,
    )


def export_sql_dump(connection: sqlite3.Connection, output_path: Path | PathLike[str]) -> Path:
    """Write SQLite SQL dump output to output_path."""
    validated = _validated_output_file_path(output_path)
    dump_text = "\n".join(connection.iterdump()) + "\n"
    validated.write_text(dump_text, "utf-8")
    return validated


def create_backup_file(db_path: Path | PathLike[str], backup_path: Path | PathLike[str]) -> Path:
    """Create a consistent SQLite backup file.

    Use SQLite's online backup API instead of copying the database file directly.
    This avoids incomplete backups when the source DB has an open connection or
    uses journal/WAL sidecar files.
    """
    source = Path(db_path).resolve()
    if not source.exists() or not source.is_file():
        raise ValidationError(f"database file does not exist: {source}")

    target = _validated_output_file_path(backup_path)
    if source == target:
        raise ValidationError("database source and backup target must be different files")

    temp_target = target.with_suffix(f"{target.suffix}.backup_tmp")
    if temp_target.exists():
        temp_target.unlink()

    try:
        source_connection = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
        target_connection = sqlite3.connect(temp_target)
        try:
            source_connection.backup(target_connection)
            target_connection.commit()
        finally:
            target_connection.close()
            source_connection.close()
        temp_target.replace(target)
    finally:
        if temp_target.exists():
            temp_target.unlink()

    return target


def _validated_output_file_path(path: Path | PathLike[str]) -> Path:
    resolved = Path(path).resolve()
    if resolved.exists() and resolved.is_dir():
        raise ValidationError(f"output path points to a directory: {resolved}")

    parent = resolved.parent
    parent.mkdir(parents=True, exist_ok=True)
    if not parent.is_dir():
        raise ValidationError(f"output parent path is not a directory: {parent}")

    return resolved


def _column_names(connection: sqlite3.Connection, table_name: str) -> list[str]:
    pragma_rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [str(row[1]) for row in pragma_rows]

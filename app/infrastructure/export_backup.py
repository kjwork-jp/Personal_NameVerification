"""File export/backup helpers for SQLite-backed data."""

from __future__ import annotations

import csv
import json
import shutil
import sqlite3
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


def export_tables_to_csv(
    connection: sqlite3.Connection,
    output_dir: Path,
    *,
    table_names: tuple[str, ...] = EXPORT_TABLES,
) -> dict[str, Path]:
    """Export each table into a dedicated CSV file under output_dir."""
    output_dir = output_dir.resolve()
    if not output_dir.exists() or not output_dir.is_dir():
        raise ValidationError(f"output directory does not exist: {output_dir}")

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
    output_path: Path,
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


def export_sql_dump(connection: sqlite3.Connection, output_path: Path) -> Path:
    """Write SQLite SQL dump output to output_path."""
    validated = _validated_output_file_path(output_path)
    dump_text = "\n".join(connection.iterdump()) + "\n"
    validated.write_text(dump_text, "utf-8")
    return validated


def create_backup_file(db_path: Path, backup_path: Path) -> Path:
    """Copy sqlite DB file as backup."""
    source = db_path.resolve()
    if not source.exists() or not source.is_file():
        raise ValidationError(f"database file does not exist: {source}")

    target = _validated_output_file_path(backup_path)
    shutil.copy2(source, target)
    return target


def _validated_output_file_path(path: Path) -> Path:
    resolved = path.resolve()
    if resolved.exists() and resolved.is_dir():
        raise ValidationError(f"output path points to a directory: {resolved}")

    parent = resolved.parent
    if not parent.exists() or not parent.is_dir():
        raise ValidationError(f"output directory does not exist: {parent}")

    return resolved


def _column_names(connection: sqlite3.Connection, table_name: str) -> list[str]:
    pragma_rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [str(row[1]) for row in pragma_rows]

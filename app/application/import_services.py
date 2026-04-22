"""Application service for CSV/JSON import foundation."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from app.application.authorization import ServiceRole, require_admin
from app.infrastructure.import_data import import_from_csv_directory, import_from_json_file


class ImportService:
    """Import data into an empty SQLite DB from CSV/JSON exports.

    Notes:
        - Destructive/admin-only operation.
        - Import target DB must be empty.
    """

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute("PRAGMA foreign_keys = ON;")

    def import_csv(self, csv_dir: Path, role: ServiceRole = "admin") -> dict[str, int]:
        require_admin(role, action="import_csv")
        return import_from_csv_directory(self._connection, csv_dir)

    def import_json(self, json_path: Path, role: ServiceRole = "admin") -> dict[str, int]:
        require_admin(role, action="import_json")
        return import_from_json_file(self._connection, json_path)

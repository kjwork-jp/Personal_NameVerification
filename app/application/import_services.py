"""Application service for CSV/JSON import foundation."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.application.authorization import ServiceRole, require_admin
from app.infrastructure.import_data import import_from_csv_directory, import_from_json_file


class ImportService:
    """Import data into an empty SQLite DB from CSV/JSON exports.

    Notes:
        - Destructive/admin-only operation.
        - Import target DB must be empty.
        - Production desktop usage should pass ``database_path`` so worker-thread
          imports use a thread-local SQLite connection.
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

    def import_csv(self, csv_dir: Path, role: ServiceRole = "admin") -> dict[str, int]:
        require_admin(role, action="import_csv")
        with self._operation_connection() as connection:
            return import_from_csv_directory(connection, csv_dir)

    def import_json(self, json_path: Path, role: ServiceRole = "admin") -> dict[str, int]:
        require_admin(role, action="import_json")
        with self._operation_connection() as connection:
            return import_from_json_file(connection, json_path)

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

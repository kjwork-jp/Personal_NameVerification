from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.infrastructure.db import check_database_integrity, initialize_database


def test_initialize_database_creates_parent_directories(tmp_path: Path) -> None:
    db_path = tmp_path / "nested" / "db" / "nameverification.db"

    connection = initialize_database(db_path)
    try:
        assert db_path.exists()
        assert db_path.parent.is_dir()
        assert connection.execute("PRAGMA integrity_check;").fetchone()[0] == "ok"
    finally:
        connection.close()


def test_check_database_integrity_accepts_ok_result() -> None:
    connection = sqlite3.connect(":memory:")
    try:
        check_database_integrity(connection)
    finally:
        connection.close()


class _FakeIntegrityConnection:
    def __init__(self, rows: list[tuple[str]]) -> None:
        self.rows = rows

    def execute(self, sql: str) -> "_FakeIntegrityConnection":
        assert sql == "PRAGMA integrity_check;"
        return self

    def fetchall(self) -> list[tuple[str]]:
        return self.rows


def test_check_database_integrity_raises_on_problem() -> None:
    connection = _FakeIntegrityConnection([("row 1 missing from index sample",)])

    with pytest.raises(sqlite3.DatabaseError, match="row 1 missing"):
        check_database_integrity(connection)  # type: ignore[arg-type]

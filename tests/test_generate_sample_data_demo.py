"""Tests for demo sample data generation."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from scripts.generate_sample_data import DEMO_PASSWORDS, generate_demo_csv, generate_demo_sqlite


def _count_table(db_path: Path, table_name: str) -> int:
    connection = sqlite3.connect(db_path)
    try:
        return int(connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0])
    finally:
        connection.close()


def _table_values(db_path: Path, sql: str) -> list[tuple[object, ...]]:
    connection = sqlite3.connect(db_path)
    try:
        return list(connection.execute(sql))
    finally:
        connection.close()


def test_generate_demo_sqlite_creates_small_meaningful_database(tmp_path: Path) -> None:
    db_path = tmp_path / "demo.db"

    generate_demo_sqlite(db_path=db_path)

    assert db_path.exists()
    assert _count_table(db_path, "names") == 5
    assert _count_table(db_path, "titles") == 3
    assert _count_table(db_path, "subtitles") == 4
    assert _count_table(db_path, "name_title_links") == 5
    assert _count_table(db_path, "name_subtitle_links") == 4
    assert _count_table(db_path, "users") == 3

    users = _table_values(
        db_path,
        "SELECT operator_id, role, password_hash, password_salt FROM users ORDER BY operator_id",
    )
    assert [row[0] for row in users] == ["demo-admin", "demo-editor", "demo-viewer"]
    assert {row[1] for row in users} == {"admin", "editor", "viewer"}
    assert all(row[2] != DEMO_PASSWORDS[str(row[0])] for row in users)
    assert all(row[3] for row in users)


def test_generate_demo_csv_creates_expected_files(tmp_path: Path) -> None:
    output_dir = tmp_path / "demo_csv"

    generate_demo_csv(output_dir=output_dir)

    expected_files = {
        "names.csv",
        "titles.csv",
        "subtitles.csv",
        "name_title_links.csv",
        "name_subtitle_links.csv",
    }
    assert {path.name for path in output_dir.iterdir()} == expected_files
    assert "Alice Sample" in (output_dir / "names.csv").read_text(encoding="utf-8")
    assert "Demo Title Alpha" in (output_dir / "titles.csv").read_text(encoding="utf-8")
    assert "ALPHA-001" in (output_dir / "subtitles.csv").read_text(encoding="utf-8")

"""Tests for demo and bulk sample data generation."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from scripts.generate_sample_data import (
    DEFAULT_LINKS_PER_NAME,
    DEFAULT_NAMES,
    DEFAULT_SUBTITLES_PER_TITLE,
    DEFAULT_TITLES,
    DEMO_PASSWORDS,
    generate_csv,
    generate_demo_csv,
    generate_demo_sqlite,
    generate_sqlite,
)


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


def test_bulk_defaults_remain_performance_oriented() -> None:
    assert DEFAULT_NAMES == 1000
    assert DEFAULT_TITLES == 1000
    assert DEFAULT_SUBTITLES_PER_TITLE == 3
    assert DEFAULT_LINKS_PER_NAME == 2


def test_generate_bulk_sqlite_creates_expected_scaled_counts(tmp_path: Path) -> None:
    db_path = tmp_path / "bulk.db"

    generate_sqlite(
        db_path=db_path,
        name_count=10,
        title_count=4,
        subtitles_per_title=2,
        links_per_name=2,
    )

    assert _count_table(db_path, "names") == 10
    assert _count_table(db_path, "titles") == 4
    assert _count_table(db_path, "subtitles") == 8
    assert _count_table(db_path, "name_title_links") == 10
    assert _count_table(db_path, "name_subtitle_links") == 10


def test_generate_bulk_csv_creates_expected_large_review_files(tmp_path: Path) -> None:
    output_dir = tmp_path / "bulk_csv"

    generate_csv(
        output_dir=output_dir,
        name_count=10,
        title_count=4,
        subtitles_per_title=2,
        links_per_name=2,
    )

    assert {path.name for path in output_dir.iterdir()} == {
        "names.csv",
        "titles.csv",
        "subtitles.csv",
        "name_subtitle_links.csv",
    }
    assert "sample-name-0000001" in (output_dir / "names.csv").read_text(
        encoding="utf-8"
    )
    assert "sample-title-0000001" in (output_dir / "titles.csv").read_text(
        encoding="utf-8"
    )
    assert "SUB-0000001" in (output_dir / "subtitles.csv").read_text(
        encoding="utf-8"
    )

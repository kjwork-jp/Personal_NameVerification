"""Tests for demo and bulk sample data generation."""

from __future__ import annotations

import csv
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


def _count_query(db_path: Path, sql: str) -> int:
    connection = sqlite3.connect(db_path)
    try:
        return int(connection.execute(sql).fetchone()[0])
    finally:
        connection.close()


def _table_values(db_path: Path, sql: str) -> list[tuple[object, ...]]:
    connection = sqlite3.connect(db_path)
    try:
        return list(connection.execute(sql))
    finally:
        connection.close()


def _csv_data_row_count(path: Path) -> int:
    with path.open(encoding="utf-8", newline="") as handle:
        return sum(1 for _row in csv.reader(handle)) - 1


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
    assert _count_table(db_path, "name_subtitle_links") == 20
    assert _table_values(
        db_path,
        """
        SELECT COUNT(*)
        FROM (
            SELECT name_id, subtitle_id
            FROM name_subtitle_links
            GROUP BY name_id, subtitle_id
        )
        """,
    )[0][0] == 20


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
    assert _csv_data_row_count(output_dir / "name_subtitle_links.csv") == 20


def test_generate_bulk_sqlite_respects_medium_uat_link_volume(tmp_path: Path) -> None:
    db_path = tmp_path / "uat.db"

    generate_sqlite(
        db_path=db_path,
        name_count=80,
        title_count=18,
        subtitles_per_title=4,
        links_per_name=3,
    )

    assert _count_table(db_path, "names") == 80
    assert _count_table(db_path, "titles") == 18
    assert _count_table(db_path, "subtitles") == 72
    assert _count_table(db_path, "name_title_links") == 80
    assert _count_table(db_path, "name_subtitle_links") == 240


def test_generate_bulk_sqlite_seeds_deleted_and_change_log_review_rows(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "uat_review.db"

    generate_sqlite(
        db_path=db_path,
        name_count=80,
        title_count=18,
        subtitles_per_title=4,
        links_per_name=3,
    )

    assert _count_query(db_path, "SELECT COUNT(*) FROM names WHERE deleted_at IS NOT NULL") == 2
    assert _count_query(db_path, "SELECT COUNT(*) FROM titles WHERE deleted_at IS NOT NULL") == 1
    assert _count_query(db_path, "SELECT COUNT(*) FROM subtitles WHERE deleted_at IS NOT NULL") == 1
    assert _count_query(
        db_path,
        "SELECT COUNT(*) FROM name_title_links WHERE deleted_at IS NOT NULL",
    ) == 1
    assert _count_query(
        db_path,
        "SELECT COUNT(*) FROM name_subtitle_links WHERE deleted_at IS NOT NULL",
    ) == 3
    assert _count_table(db_path, "change_logs") == 4
    assert _table_values(
        db_path,
        "SELECT DISTINCT operator_id FROM change_logs ORDER BY operator_id",
    ) == [("uat-admin",), ("uat-editor",)]

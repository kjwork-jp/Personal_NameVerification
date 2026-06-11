"""Tests for normalized title/subtitle display-name expression indexes."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.infrastructure.db import ensure_display_name_unique_indexes, initialize_database


def test_title_display_name_index_uses_app_normalization(tmp_path: Path) -> None:
    connection = initialize_database(tmp_path / "display-name-index.db")
    try:
        connection.execute("INSERT INTO titles(title_name) VALUES (?)", ("Demo Title",))
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("INSERT INTO titles(title_name) VALUES (?)", (" demo　title ",))
    finally:
        connection.close()


def test_subtitle_display_name_index_uses_app_normalization_per_title(tmp_path: Path) -> None:
    connection = initialize_database(tmp_path / "subtitle-display-name-index.db")
    try:
        first_title = connection.execute(
            "INSERT INTO titles(title_name) VALUES (?)",
            ("Main",),
        ).lastrowid
        second_title = connection.execute(
            "INSERT INTO titles(title_name) VALUES (?)",
            ("Other",),
        ).lastrowid
        assert first_title is not None
        assert second_title is not None

        connection.execute(
            """
            INSERT INTO subtitles(title_id, subtitle_code, subtitle_name)
            VALUES (?, ?, ?)
            """,
            (first_title, "S1", "Same Name"),
        )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO subtitles(title_id, subtitle_code, subtitle_name)
                VALUES (?, ?, ?)
                """,
                (first_title, "S2", " same　name "),
            )
        connection.execute(
            """
            INSERT INTO subtitles(title_id, subtitle_code, subtitle_name)
            VALUES (?, ?, ?)
            """,
            (second_title, "S1", " same name "),
        )
    finally:
        connection.close()


def test_deleted_display_name_duplicates_do_not_block_active_index(tmp_path: Path) -> None:
    connection = initialize_database(tmp_path / "deleted-display-name-index.db")
    try:
        connection.execute("INSERT INTO titles(title_name) VALUES (?)", ("Demo Title",))
        connection.execute(
            "INSERT INTO titles(title_name, deleted_at) VALUES (?, ?)",
            (" demo　title ", "2026-01-01T00:00:00Z"),
        )
        assert connection.execute("SELECT COUNT(*) FROM titles").fetchone()[0] == 2
    finally:
        connection.close()


def test_index_readiness_error_includes_safe_blocker_details(tmp_path: Path) -> None:
    connection = initialize_database(tmp_path / "readiness-details.db")
    try:
        connection.execute("DROP INDEX IF EXISTS uq_titles_active_display_name")
        connection.execute("INSERT INTO titles(title_name) VALUES (?)", ("Demo Title",))
        connection.execute("INSERT INTO titles(title_name) VALUES (?)", (" demo　title ",))

        with pytest.raises(sqlite3.IntegrityError) as exc_info:
            ensure_display_name_unique_indexes(connection)

        message = str(exc_info.value)
        assert "title/subtitle display-name index readiness failed" in message
        assert "title_groups=1" in message
        assert "key='demo title'" in message
        assert "ids=(1, 2)" in message
        assert "display_names=('Demo Title', ' demo　title ')" in message
    finally:
        connection.close()

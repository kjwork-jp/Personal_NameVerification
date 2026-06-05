"""Schema-level duplicate display-name constraint tests."""

from __future__ import annotations

import sqlite3

import pytest

from app.infrastructure.db import apply_schema


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    apply_schema(connection)
    return connection


def test_titles_reject_duplicate_active_trimmed_casefolded_names() -> None:
    connection = _connection()
    connection.execute("INSERT INTO titles(title_name) VALUES (?)", (" Main Title ",))

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("INSERT INTO titles(title_name) VALUES (?)", ("main title",))


def test_titles_allow_reuse_after_logical_delete() -> None:
    connection = _connection()
    connection.execute("INSERT INTO titles(title_name, deleted_at) VALUES (?, ?)", ("Main", "x"))

    connection.execute("INSERT INTO titles(title_name) VALUES (?)", (" main ",))

    rows = connection.execute("SELECT title_name FROM titles ORDER BY id").fetchall()
    assert [row["title_name"] for row in rows] == ["Main", " main "]


def test_subtitles_reject_duplicate_active_trimmed_casefolded_names_per_title() -> None:
    connection = _connection()
    title_id = _insert_title(connection, "Main")
    connection.execute(
        "INSERT INTO subtitles(title_id, subtitle_code, subtitle_name) VALUES (?, ?, ?)",
        (title_id, "S1", " Sub Name "),
    )

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO subtitles(title_id, subtitle_code, subtitle_name) VALUES (?, ?, ?)",
            (title_id, "S2", "sub name"),
        )


def test_subtitles_allow_same_name_under_different_titles() -> None:
    connection = _connection()
    first_title_id = _insert_title(connection, "First")
    second_title_id = _insert_title(connection, "Second")

    connection.execute(
        "INSERT INTO subtitles(title_id, subtitle_code, subtitle_name) VALUES (?, ?, ?)",
        (first_title_id, "S1", "Sub Name"),
    )
    connection.execute(
        "INSERT INTO subtitles(title_id, subtitle_code, subtitle_name) VALUES (?, ?, ?)",
        (second_title_id, "S1", " sub name "),
    )

    rows = connection.execute("SELECT COUNT(1) FROM subtitles").fetchone()
    assert int(rows[0]) == 2


def test_subtitles_allow_reuse_after_logical_delete() -> None:
    connection = _connection()
    title_id = _insert_title(connection, "Main")
    connection.execute(
        """
        INSERT INTO subtitles(title_id, subtitle_code, subtitle_name, deleted_at)
        VALUES (?, ?, ?, ?)
        """,
        (title_id, "S1", "Sub Name", "x"),
    )

    connection.execute(
        "INSERT INTO subtitles(title_id, subtitle_code, subtitle_name) VALUES (?, ?, ?)",
        (title_id, "S2", " sub name "),
    )

    rows = connection.execute("SELECT subtitle_name FROM subtitles ORDER BY id").fetchall()
    assert [row["subtitle_name"] for row in rows] == ["Sub Name", " sub name "]


def _insert_title(connection: sqlite3.Connection, title_name: str) -> int:
    cursor = connection.execute("INSERT INTO titles(title_name) VALUES (?)", (title_name,))
    lastrowid = cursor.lastrowid
    assert lastrowid is not None
    return int(lastrowid)

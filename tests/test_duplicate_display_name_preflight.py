"""Tests for duplicate display-name preflight reports."""

from __future__ import annotations

import sqlite3

from app.application.duplicate_display_name_preflight import inspect_duplicate_display_names
from app.application.core_services import CoreService, TitleInput
from app.infrastructure.db import apply_schema


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    apply_schema(connection)
    return connection


def test_preflight_reports_active_title_duplicates_by_normalized_display_name() -> None:
    connection = _connection()
    _insert_title(connection, "Demo Title")
    _insert_title(connection, " demo　title ")
    _insert_title(connection, "Deleted Duplicate", deleted_at="2026-01-01T00:00:00Z")
    _insert_title(connection, " deleted duplicate ", deleted_at="2026-01-02T00:00:00Z")

    report = inspect_duplicate_display_names(connection)

    assert report.has_blockers is True
    assert report.blocker_count == 1
    group = report.title_duplicates[0]
    assert group.entity_type == "title"
    assert group.normalized_key == "demo title"
    assert group.ids == (1, 2)
    assert group.display_names == ("Demo Title", " demo　title ")
    assert group.title_id is None
    assert report.subtitle_duplicates == ()


def test_preflight_reports_active_subtitle_duplicates_per_title_only() -> None:
    connection = _connection()
    service = CoreService(connection)
    first_title_id = service.create_title(TitleInput(title_name="Main"), operator_id="op-1")
    second_title_id = service.create_title(TitleInput(title_name="Other"), operator_id="op-1")
    _insert_subtitle(connection, first_title_id, "S1", "Same Name")
    _insert_subtitle(connection, first_title_id, "S2", " same　name ")
    _insert_subtitle(connection, second_title_id, "S1", "same name")
    _insert_subtitle(
        connection,
        first_title_id,
        "S3",
        " same name ",
        deleted_at="2026-01-01T00:00:00Z",
    )

    report = inspect_duplicate_display_names(connection)

    assert report.has_blockers is True
    assert report.blocker_count == 1
    assert report.title_duplicates == ()
    group = report.subtitle_duplicates[0]
    assert group.entity_type == "subtitle"
    assert group.normalized_key == "same name"
    assert group.title_id == first_title_id
    assert group.ids == (1, 2)
    assert group.display_names == ("Same Name", " same　name ")


def test_preflight_passes_without_active_display_name_duplicates() -> None:
    connection = _connection()
    service = CoreService(connection)
    first_title_id = service.create_title(TitleInput(title_name="Main"), operator_id="op-1")
    second_title_id = service.create_title(TitleInput(title_name="Other"), operator_id="op-1")
    _insert_subtitle(connection, first_title_id, "S1", "Name")
    _insert_subtitle(connection, second_title_id, "S1", " name ")

    report = inspect_duplicate_display_names(connection)

    assert report.has_blockers is False
    assert report.blocker_count == 0
    assert report.title_duplicates == ()
    assert report.subtitle_duplicates == ()


def _insert_title(
    connection: sqlite3.Connection,
    title_name: str,
    *,
    deleted_at: str | None = None,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO titles(title_name, deleted_at, created_at, updated_at)
        VALUES (?, ?, '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')
        """,
        (title_name, deleted_at),
    )
    lastrowid = cursor.lastrowid
    assert lastrowid is not None
    connection.commit()
    return int(lastrowid)


def _insert_subtitle(
    connection: sqlite3.Connection,
    title_id: int,
    subtitle_code: str,
    subtitle_name: str,
    *,
    deleted_at: str | None = None,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO subtitles(
            title_id, subtitle_code, subtitle_name, sort_order, deleted_at, created_at, updated_at
        ) VALUES (?, ?, ?, 0, ?, '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')
        """,
        (title_id, subtitle_code, subtitle_name, deleted_at),
    )
    lastrowid = cursor.lastrowid
    assert lastrowid is not None
    connection.commit()
    return int(lastrowid)

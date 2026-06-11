"""Duplicate display-name validation tests for CoreService."""

from __future__ import annotations

import sqlite3

import pytest

from app.application.core_services import CoreService, SubtitleInput, TitleInput
from app.domain.errors import ConflictError, ValidationError
from app.infrastructure.db import apply_schema


def _service() -> tuple[sqlite3.Connection, CoreService]:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    apply_schema(connection)
    return connection, CoreService(connection)


def test_write_operations_start_begin_immediate() -> None:
    connection, service = _service()
    statements: list[str] = []
    connection.set_trace_callback(statements.append)

    service.create_title(TitleInput(title_name="Atomic"), operator_id="op-1")

    assert any(statement.upper().startswith("BEGIN IMMEDIATE") for statement in statements)


def test_title_duplicate_is_rejected_by_project_normalization() -> None:
    _, service = _service()
    first_id = service.create_title(TitleInput(title_name=" Ｄｅｍｏ　Title "), operator_id="op-1")

    with pytest.raises(ConflictError, match="title already exists"):
        service.create_title(TitleInput(title_name="demo title"), operator_id="op-1")

    service.update_title(first_id, TitleInput(title_name="DEMO TITLE"), operator_id="op-1")


def test_title_duplicate_ignores_deleted_until_restore() -> None:
    _, service = _service()
    deleted_id = service.create_title(TitleInput(title_name="Reusable"), operator_id="op-1")
    service.delete_title(deleted_id, operator_id="op-1")

    service.create_title(TitleInput(title_name=" reusable "), operator_id="op-1")

    with pytest.raises(ConflictError, match="title already exists"):
        service.restore_title(deleted_id, operator_id="op-1")


def test_title_blank_input_is_validation_error() -> None:
    _, service = _service()

    with pytest.raises(ValidationError, match="title_name must not be blank"):
        service.create_title(TitleInput(title_name="   "), operator_id="op-1")


def test_title_scan_ignores_legacy_blank_rows() -> None:
    connection, service = _service()
    connection.execute(
        """
        INSERT INTO titles(title_name, created_at, updated_at)
        VALUES (?, '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')
        """,
        ("   ",),
    )
    connection.commit()

    title_id = service.create_title(TitleInput(title_name="Valid"), operator_id="op-1")

    assert isinstance(title_id, int)


def test_title_metadata_edit_allows_unchanged_legacy_duplicate_display_name() -> None:
    connection, service = _service()
    _drop_display_name_indexes(connection)
    first_id = _insert_title(connection, "Legacy Duplicate")
    _insert_title(connection, " legacy duplicate ")

    service.update_title(
        first_id,
        TitleInput(title_name="Legacy Duplicate", note="metadata only"),
        operator_id="op-1",
    )

    row = connection.execute("SELECT note FROM titles WHERE id = ?", (first_id,)).fetchone()
    assert row["note"] == "metadata only"


def test_subtitle_duplicate_is_rejected_per_title_by_project_normalization() -> None:
    _, service = _service()
    first_title_id = service.create_title(TitleInput(title_name="Main"), operator_id="op-1")
    second_title_id = service.create_title(TitleInput(title_name="Other"), operator_id="op-1")
    first_subtitle_id = service.create_subtitle(
        SubtitleInput(title_id=first_title_id, subtitle_code="S1", subtitle_name=" Sub  Name "),
        operator_id="op-1",
    )

    with pytest.raises(ConflictError, match="subtitle already exists for title"):
        service.create_subtitle(
            SubtitleInput(title_id=first_title_id, subtitle_code="S2", subtitle_name="sub name"),
            operator_id="op-1",
        )

    service.create_subtitle(
        SubtitleInput(title_id=second_title_id, subtitle_code="S1", subtitle_name="sub name"),
        operator_id="op-1",
    )
    service.update_subtitle(
        first_subtitle_id,
        SubtitleInput(title_id=first_title_id, subtitle_code="S1", subtitle_name="SUB NAME"),
        operator_id="op-1",
    )


def test_subtitle_duplicate_ignores_deleted_until_restore() -> None:
    _, service = _service()
    title_id = service.create_title(TitleInput(title_name="Main"), operator_id="op-1")
    deleted_id = service.create_subtitle(
        SubtitleInput(title_id=title_id, subtitle_code="S1", subtitle_name="Reusable"),
        operator_id="op-1",
    )
    service.delete_subtitle(deleted_id, operator_id="op-1")

    service.create_subtitle(
        SubtitleInput(title_id=title_id, subtitle_code="S2", subtitle_name=" reusable "),
        operator_id="op-1",
    )

    with pytest.raises(ConflictError, match="subtitle already exists for title"):
        service.restore_subtitle(deleted_id, operator_id="op-1")


def test_subtitle_blank_input_is_validation_error() -> None:
    _, service = _service()
    title_id = service.create_title(TitleInput(title_name="Main"), operator_id="op-1")

    with pytest.raises(ValidationError, match="subtitle_name must not be blank"):
        service.create_subtitle(
            SubtitleInput(title_id=title_id, subtitle_code="S1", subtitle_name="   "),
            operator_id="op-1",
        )


def test_subtitle_scan_ignores_legacy_blank_rows() -> None:
    connection, service = _service()
    title_id = service.create_title(TitleInput(title_name="Main"), operator_id="op-1")
    connection.execute(
        """
        INSERT INTO subtitles(
            title_id, subtitle_code, subtitle_name, sort_order, created_at, updated_at
        ) VALUES (?, 'S1', ?, 0, '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')
        """,
        (title_id, "   "),
    )
    connection.commit()

    subtitle_id = service.create_subtitle(
        SubtitleInput(title_id=title_id, subtitle_code="S2", subtitle_name="Valid"),
        operator_id="op-1",
    )

    assert isinstance(subtitle_id, int)


def test_subtitle_metadata_edit_allows_unchanged_legacy_duplicate_display_name() -> None:
    connection, service = _service()
    _drop_display_name_indexes(connection)
    title_id = service.create_title(TitleInput(title_name="Main"), operator_id="op-1")
    first_id = _insert_subtitle(connection, title_id, "S1", "Legacy Duplicate")
    _insert_subtitle(connection, title_id, "S2", " legacy duplicate ")

    service.update_subtitle(
        first_id,
        SubtitleInput(
            title_id=title_id,
            subtitle_code="S1",
            subtitle_name="Legacy Duplicate",
            note="metadata only",
        ),
        operator_id="op-1",
    )

    row = connection.execute("SELECT note FROM subtitles WHERE id = ?", (first_id,)).fetchone()
    assert row["note"] == "metadata only"


def _drop_display_name_indexes(connection: sqlite3.Connection) -> None:
    connection.execute("DROP INDEX IF EXISTS uq_titles_active_display_name")
    connection.execute("DROP INDEX IF EXISTS uq_subtitles_active_title_display_name")
    connection.commit()


def _insert_title(connection: sqlite3.Connection, title_name: str) -> int:
    cursor = connection.execute(
        """
        INSERT INTO titles(title_name, created_at, updated_at)
        VALUES (?, '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')
        """,
        (title_name,),
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
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO subtitles(
            title_id, subtitle_code, subtitle_name, sort_order, created_at, updated_at
        ) VALUES (?, ?, ?, 0, '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')
        """,
        (title_id, subtitle_code, subtitle_name),
    )
    lastrowid = cursor.lastrowid
    assert lastrowid is not None
    connection.commit()
    return int(lastrowid)

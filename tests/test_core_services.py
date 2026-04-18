"""Tests for core application services."""

from __future__ import annotations

import sqlite3

import pytest

from app.application.core_services import CoreService, NameInput, SubtitleInput, TitleInput
from app.domain.errors import ConflictError, NotFoundError, StateTransitionError
from app.infrastructure.db import apply_schema


def _service() -> tuple[sqlite3.Connection, CoreService]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    apply_schema(conn)
    return conn, CoreService(conn)


def test_name_crud_lifecycle_with_normalization() -> None:
    conn, service = _service()

    name_id = service.create_name(NameInput(raw_name=" Ａｌｉｃｅ "), operator_id="op-1")
    row = conn.execute(
        "SELECT raw_name, normalized_name, deleted_at FROM names WHERE id = ?", (name_id,)
    ).fetchone()
    assert row["raw_name"] == " Ａｌｉｃｅ "
    assert row["normalized_name"] == "alice"
    assert row["deleted_at"] is None

    service.update_name(name_id, NameInput(raw_name="Alice Updated"), operator_id="op-1")
    updated = conn.execute("SELECT raw_name FROM names WHERE id = ?", (name_id,)).fetchone()
    assert updated["raw_name"] == "Alice Updated"

    service.delete_name(name_id, operator_id="op-1")
    deleted = conn.execute("SELECT deleted_at FROM names WHERE id = ?", (name_id,)).fetchone()
    assert deleted["deleted_at"] is not None

    service.restore_name(name_id, operator_id="op-1")
    restored = conn.execute("SELECT deleted_at FROM names WHERE id = ?", (name_id,)).fetchone()
    assert restored["deleted_at"] is None

    service.delete_name(name_id, operator_id="op-1")
    service.hard_delete_name(name_id, operator_id="op-1")
    with pytest.raises(NotFoundError):
        service.update_name(name_id, NameInput(raw_name="x"), operator_id="op-1")


def test_name_conflict_is_mapped_to_conflict_error() -> None:
    _, service = _service()
    service.create_name(NameInput(raw_name="Alice"), operator_id="op-1")

    with pytest.raises(ConflictError):
        service.create_name(NameInput(raw_name="ＡＬＩＣＥ"), operator_id="op-1")


def test_title_subtitle_and_link_lifecycle() -> None:
    conn, service = _service()
    name_id = service.create_name(NameInput(raw_name="Alice"), operator_id="op-1")

    title_id = service.create_title(TitleInput(title_name="Main"), operator_id="op-1")
    subtitle_id = service.create_subtitle(
        SubtitleInput(title_id=title_id, subtitle_code="S1", subtitle_name="Sub 1"),
        operator_id="op-1",
    )

    link_id = service.link_name_to_subtitle(
        name_id=name_id,
        subtitle_id=subtitle_id,
        relation_type="primary",
        operator_id="op-1",
    )

    linked = conn.execute(
        "SELECT deleted_at, relation_type FROM name_subtitle_links WHERE id = ?", (link_id,)
    ).fetchone()
    assert linked["deleted_at"] is None
    assert linked["relation_type"] == "primary"

    service.unlink_name_from_subtitle(link_id=link_id, operator_id="op-1")
    unlinked = conn.execute(
        "SELECT deleted_at FROM name_subtitle_links WHERE id = ?", (link_id,)
    ).fetchone()
    assert unlinked["deleted_at"] is not None

    restored_link_id = service.link_name_to_subtitle(
        name_id=name_id,
        subtitle_id=subtitle_id,
        relation_type="secondary",
        operator_id="op-1",
    )
    assert restored_link_id == link_id


def test_hard_delete_requires_logical_delete_first() -> None:
    _, service = _service()
    title_id = service.create_title(TitleInput(title_name="Main"), operator_id="op-1")

    with pytest.raises(StateTransitionError):
        service.hard_delete_title(title_id=title_id, operator_id="op-1")


def test_subtitle_unique_conflict() -> None:
    _, service = _service()
    title_id = service.create_title(TitleInput(title_name="Main"), operator_id="op-1")

    service.create_subtitle(
        SubtitleInput(title_id=title_id, subtitle_code="S1", subtitle_name="Sub 1"),
        operator_id="op-1",
    )

    with pytest.raises(ConflictError):
        service.create_subtitle(
            SubtitleInput(title_id=title_id, subtitle_code="S1", subtitle_name="Another"),
            operator_id="op-1",
        )

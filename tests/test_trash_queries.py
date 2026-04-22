"""Tests for deleted(trash) query listings."""

from __future__ import annotations

import sqlite3

from app.application.core_services import CoreService, NameInput, SubtitleInput, TitleInput
from app.application.query_services import QueryService
from app.infrastructure.db import apply_schema


def _services() -> tuple[sqlite3.Connection, CoreService, QueryService]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    apply_schema(conn)
    return conn, CoreService(conn), QueryService(conn)


def test_list_deleted_entities_and_links() -> None:
    _, core, query = _services()

    name_id = core.create_name(NameInput(raw_name="Alice"), operator_id="op")
    title_id = core.create_title(TitleInput(title_name="Title"), operator_id="op")
    subtitle_id = core.create_subtitle(
        SubtitleInput(title_id=title_id, subtitle_code="S1", subtitle_name="Subtitle"),
        operator_id="op",
    )
    link_id = core.link_name_to_subtitle(
        name_id, subtitle_id, relation_type="primary", operator_id="op"
    )

    core.unlink_name_from_subtitle(link_id, operator_id="op")
    core.delete_subtitle(subtitle_id, operator_id="op")
    core.delete_title(title_id, operator_id="op")
    core.delete_name(name_id, operator_id="op")

    assert [row.id for row in query.list_deleted_names()] == [name_id]
    assert [row.id for row in query.list_deleted_titles()] == [title_id]
    assert [row.id for row in query.list_deleted_subtitles()] == [subtitle_id]
    assert [row.link_id for row in query.list_deleted_links()] == [link_id]

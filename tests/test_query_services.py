"""Tests for search/read query services."""

from __future__ import annotations

import sqlite3

import pytest

from app.application.core_services import CoreService, NameInput, SubtitleInput, TitleInput
from app.application.query_services import QueryService
from app.domain.errors import AuthorizationError
from app.infrastructure.db import apply_schema


def _services() -> tuple[sqlite3.Connection, CoreService, QueryService]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    apply_schema(conn)
    return conn, CoreService(conn), QueryService(conn)


def test_search_names_exact_and_partial() -> None:
    _, core, query = _services()
    core.create_name(NameInput(raw_name="Alice"), operator_id="op")
    core.create_name(NameInput(raw_name="ALICE COOPER"), operator_id="op")

    exact = query.search_names("alice", exact_match=True)
    assert [row.raw_name for row in exact] == ["Alice"]

    partial = query.search_names("alice", exact_match=False)
    assert [row.raw_name for row in partial] == ["ALICE COOPER", "Alice"]


def test_search_names_with_title_filter_and_has_links() -> None:
    _, core, query = _services()

    name_a = core.create_name(NameInput(raw_name="Alice"), operator_id="op")
    name_b = core.create_name(NameInput(raw_name="Bob"), operator_id="op")

    title_1 = core.create_title(TitleInput(title_name="T1"), operator_id="op")
    title_2 = core.create_title(TitleInput(title_name="T2"), operator_id="op")

    subtitle_1 = core.create_subtitle(
        SubtitleInput(title_id=title_1, subtitle_code="S1", subtitle_name="S1"), operator_id="op"
    )
    subtitle_2 = core.create_subtitle(
        SubtitleInput(title_id=title_2, subtitle_code="S2", subtitle_name="S2"), operator_id="op"
    )

    core.link_name_to_subtitle(name_a, subtitle_1, relation_type="primary", operator_id="op")
    core.link_name_to_subtitle(name_b, subtitle_2, relation_type="primary", operator_id="op")

    filtered_title_1 = query.search_names(title_id=title_1)
    assert [row.raw_name for row in filtered_title_1] == ["Alice"]

    has_links = query.search_names(has_links=True)
    assert [row.raw_name for row in has_links] == ["Bob", "Alice"]

    no_links_name = core.create_name(NameInput(raw_name="Charlie"), operator_id="op")
    assert isinstance(no_links_name, int)
    no_links = query.search_names(has_links=False)
    assert [row.raw_name for row in no_links] == ["Charlie"]


def test_get_detail_and_related_rows() -> None:
    _, core, query = _services()

    name_id = core.create_name(NameInput(raw_name="Alice"), operator_id="op")
    title_id = core.create_title(TitleInput(title_name="Title"), operator_id="op")
    subtitle_id = core.create_subtitle(
        SubtitleInput(title_id=title_id, subtitle_code="S1", subtitle_name="Subtitle"),
        operator_id="op",
    )
    core.link_name_to_subtitle(name_id, subtitle_id, relation_type="primary", operator_id="op")

    name_detail = query.get_name_detail(name_id)
    assert name_detail.raw_name == "Alice"

    title_detail = query.get_title_detail(title_id)
    assert title_detail.title_name == "Title"

    subtitle_detail = query.get_subtitle_detail(subtitle_id)
    assert subtitle_detail.subtitle_name == "Subtitle"

    related_rows = query.list_related_rows(name_id)
    assert len(related_rows) == 1
    assert related_rows[0].relation_type == "primary"


def test_query_service_rejects_unknown_role() -> None:
    _, core, query = _services()
    core.create_name(NameInput(raw_name="Alice"), operator_id="op")

    with pytest.raises(AuthorizationError):
        query.search_names("Alice", role="invalid-role")  # type: ignore[arg-type]

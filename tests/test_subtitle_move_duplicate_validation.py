"""Subtitle move duplicate validation regression tests."""

from __future__ import annotations

import sqlite3

import pytest

from app.application.core_services import CoreService, SubtitleInput, TitleInput
from app.domain.errors import ConflictError
from app.infrastructure.db import apply_schema


def test_subtitle_move_rechecks_duplicate_display_name_in_destination_title() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    apply_schema(connection)
    service = CoreService(connection)

    source_title_id = service.create_title(TitleInput(title_name="Source"), operator_id="op-1")
    destination_title_id = service.create_title(
        TitleInput(title_name="Destination"), operator_id="op-1"
    )
    moving_subtitle_id = service.create_subtitle(
        SubtitleInput(
            title_id=source_title_id,
            subtitle_code="S1",
            subtitle_name="Shared Name",
        ),
        operator_id="op-1",
    )
    service.create_subtitle(
        SubtitleInput(
            title_id=destination_title_id,
            subtitle_code="S1",
            subtitle_name=" shared name ",
        ),
        operator_id="op-1",
    )

    with pytest.raises(ConflictError, match="subtitle already exists for title"):
        service.update_subtitle(
            moving_subtitle_id,
            SubtitleInput(
                title_id=destination_title_id,
                subtitle_code="S2",
                subtitle_name="Shared Name",
            ),
            operator_id="op-1",
        )

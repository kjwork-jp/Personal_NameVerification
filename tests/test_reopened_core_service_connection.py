"""Regression coverage for CoreService on reopened SQLite connections."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from app.application.core_services import CoreService, SubtitleInput, TitleInput
from app.infrastructure.db import initialize_database


def test_core_service_registers_functions_on_reopened_connection(tmp_path: Path) -> None:
    db_path = tmp_path / "reopened.db"
    initialized = initialize_database(db_path)
    initialized.close()

    reopened = sqlite3.connect(db_path)
    reopened.row_factory = sqlite3.Row
    try:
        service = CoreService(reopened)
        title_id = service.create_title(TitleInput(title_name="Main"), operator_id="op-1")
        subtitle_id = service.create_subtitle(
            SubtitleInput(title_id=title_id, subtitle_code="S1", subtitle_name="First"),
            operator_id="op-1",
        )

        assert title_id > 0
        assert subtitle_id > 0
    finally:
        reopened.close()

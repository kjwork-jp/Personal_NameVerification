"""Tests for Data I/O presentation copy."""

from __future__ import annotations

from app.ui.operations_guidance import (
    DATA_IO_GROUP_DESCRIPTIONS,
    DATA_IO_LOG_DESCRIPTION,
    DATA_IO_PAGE_DESCRIPTION,
    DATA_IO_PAGE_TITLE,
    DATA_IO_RESULT_DESCRIPTION,
)


def test_data_io_page_copy_is_defined() -> None:
    assert DATA_IO_PAGE_TITLE == "Data I/O"
    assert "Export" in DATA_IO_PAGE_DESCRIPTION
    assert "Backup" in DATA_IO_PAGE_DESCRIPTION
    assert "Restore" in DATA_IO_PAGE_DESCRIPTION
    assert "Import" in DATA_IO_PAGE_DESCRIPTION


def test_data_io_group_descriptions_cover_core_operations() -> None:
    assert set(DATA_IO_GROUP_DESCRIPTIONS) == {"Export", "Backup", "Restore", "Import"}
    assert "review" in DATA_IO_GROUP_DESCRIPTIONS["Export"]
    assert "SQLite" in DATA_IO_GROUP_DESCRIPTIONS["Backup"]
    assert "Admin-only" in DATA_IO_GROUP_DESCRIPTIONS["Restore"]
    assert "Admin-only" in DATA_IO_GROUP_DESCRIPTIONS["Import"]


def test_data_io_secondary_copy_is_defined() -> None:
    assert "OK/ERROR" in DATA_IO_RESULT_DESCRIPTION
    assert "filtered" in DATA_IO_LOG_DESCRIPTION
    assert "exported" in DATA_IO_LOG_DESCRIPTION

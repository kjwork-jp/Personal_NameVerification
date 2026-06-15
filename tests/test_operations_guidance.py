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
    assert DATA_IO_PAGE_TITLE == "データ入出力"
    assert "データ出力" in DATA_IO_PAGE_DESCRIPTION
    assert "バックアップ" in DATA_IO_PAGE_DESCRIPTION
    assert "復元" in DATA_IO_PAGE_DESCRIPTION
    assert "データ取込" in DATA_IO_PAGE_DESCRIPTION


def test_data_io_group_descriptions_cover_core_operations() -> None:
    assert set(DATA_IO_GROUP_DESCRIPTIONS) == {"データ出力", "バックアップ", "復元", "データ取込"}
    assert "出力" in DATA_IO_GROUP_DESCRIPTIONS["データ出力"]
    assert "SQLite" in DATA_IO_GROUP_DESCRIPTIONS["バックアップ"]
    assert "管理者専用操作" in DATA_IO_GROUP_DESCRIPTIONS["復元"]
    assert "管理者専用操作" in DATA_IO_GROUP_DESCRIPTIONS["データ取込"]


def test_data_io_secondary_copy_is_defined() -> None:
    assert "OK" in DATA_IO_RESULT_DESCRIPTION
    assert "ERROR" in DATA_IO_RESULT_DESCRIPTION
    assert "絞り込み" in DATA_IO_LOG_DESCRIPTION
    assert "出力" in DATA_IO_LOG_DESCRIPTION

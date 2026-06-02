"""UI tests for the focused subtitle management tab."""

from __future__ import annotations

import os

import pytest

from app.application.read_models import NameSearchRow, NameTitleLinkRow, SubtitleDetail, TitleDetail

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui.role_context import RoleContext  # noqa: E402
from app.ui.subtitle_management_tab import SubtitleManagementTab  # noqa: E402


class StubCoreService:
    pass


class StubQueryService:
    def __init__(self) -> None:
        self.titles = [
            TitleDetail(
                id=1,
                title_name="Alpha Title",
                note=None,
                icon_path=None,
                deleted_at=None,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            ),
            TitleDetail(
                id=2,
                title_name="Beta Title",
                note=None,
                icon_path=None,
                deleted_at=None,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            ),
        ]

    def search_names(self, *args, **kwargs) -> list[NameSearchRow]:  # type: ignore[no-untyped-def]
        _ = (args, kwargs)
        return []

    def list_names_for_title(
        self,
        title_id: int,
        role: str = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[NameTitleLinkRow]:
        _ = (title_id, role, include_deleted)
        return []

    def list_titles(
        self,
        role: str = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[TitleDetail]:
        _ = (role, include_deleted)
        return self.titles

    def list_subtitles(
        self,
        title_id: int,
        role: str = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[SubtitleDetail]:
        _ = (role, include_deleted)
        rows = [
            SubtitleDetail(
                id=10 + title_id,
                title_id=title_id,
                subtitle_code=f"S{title_id}",
                subtitle_name=f"{'Alpha' if title_id == 1 else 'Beta'} Subtitle",
                sort_order=title_id,
                note="primary" if title_id == 1 else "secondary",
                icon_path=None,
                deleted_at=None,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            )
        ]
        if title_id == 2:
            rows.append(
                SubtitleDetail(
                    id=30,
                    title_id=2,
                    subtitle_code="S2D",
                    subtitle_name="Beta Deleted Subtitle",
                    sort_order=20,
                    note="deleted secondary",
                    icon_path=None,
                    deleted_at="2026-01-02T00:00:00Z",
                    created_at="2026-01-01T00:00:00Z",
                    updated_at="2026-01-02T00:00:00Z",
                )
            )
        return rows


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _subtitle_tab() -> SubtitleManagementTab:
    _app()
    return SubtitleManagementTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(),
        role_context=RoleContext(role="admin", operator_id="op-1"),
    )


def test_subtitle_list_has_cross_parent_search_box() -> None:
    tab = _subtitle_tab()

    assert tab.subtitle_list_search_input.property("cross_parent_subtitle_search") is True
    assert tab.subtitle_list_table.property("cross_parent_subtitle_list") is True
    assert tab.subtitle_list_table.rowCount() == 3

    tab.subtitle_list_search_input.setText("beta")

    assert tab.subtitle_list_table.property("filtered_cross_parent_subtitle_rows") is True
    assert tab.subtitle_list_table.rowCount() == 2
    assert tab.subtitle_list_table.item(0, 1).text() == "Beta Title"
    assert tab.subtitle_list_table.item(0, 3).text() == "Beta Subtitle"


def test_subtitle_list_search_matches_notes_and_status() -> None:
    tab = _subtitle_tab()

    tab.subtitle_list_search_input.setText("primary")

    assert tab.subtitle_list_table.rowCount() == 1
    assert tab.subtitle_list_table.item(0, 1).text() == "Alpha Title"
    assert tab.subtitle_list_table.item(0, 7).text() == "primary"
    assert tab.subtitle_list_table.item(0, 7).toolTip() == "primary"


def test_subtitle_list_summary_shows_totals_filtered_and_selection_count() -> None:
    tab = _subtitle_tab()

    summary = tab.subtitle_list_summary_label.text()
    assert "一覧 3件" in summary
    assert "表示中 3件" in summary
    assert "選択中 0件" in summary
    assert "有効 2件" in summary
    assert "削除済み 1件" in summary
    assert "親タイトル 2件" in summary

    tab.subtitle_list_search_input.setText("deleted")

    filtered_summary = tab.subtitle_list_summary_label.text()
    assert "一覧 3件" in filtered_summary
    assert "表示中 1件" in filtered_summary
    assert "有効 0件" in filtered_summary
    assert "削除済み 1件" in filtered_summary
    assert "親タイトル 1件" in filtered_summary

    tab.subtitle_list_table.selectRow(0)

    assert "選択中 1件" in tab.subtitle_list_summary_label.text()

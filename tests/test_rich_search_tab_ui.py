"""Regression tests for Rich Admin UI search tab summaries."""

from __future__ import annotations

import os

import pytest

from app.application.read_models import NameDetail, NameSearchRow, RelatedRow

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication
qt_core = pytest.importorskip("PySide6.QtCore", exc_type=ImportError)
QItemSelectionModel = qt_core.QItemSelectionModel

from app.ui.rich_search_tab import SearchTab  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402


class StubSearchQueryService:
    def search_names(self, *args, **kwargs) -> list[NameSearchRow]:  # type: ignore[no-untyped-def]
        _ = (args, kwargs)
        return [
            NameSearchRow(
                id=1,
                raw_name="Alice",
                normalized_name="alice",
                note="primary",
                deleted_at=None,
                linked_count=2,
                title_ids=(10,),
                public_id="name-public-id-1",
                title_related_count=1,
                subtitle_related_count=1,
            ),
            NameSearchRow(
                id=2,
                raw_name="Deleted Bob",
                normalized_name="deleted bob",
                note=None,
                deleted_at="2026-01-01T00:00:00Z",
                linked_count=0,
                title_ids=(),
                public_id="name-public-id-2",
                title_related_count=0,
                subtitle_related_count=0,
            ),
        ]

    def get_name_detail(self, name_id: int, role: str = "admin") -> NameDetail:
        _ = role
        return NameDetail(
            id=name_id,
            raw_name="Alice" if name_id == 1 else "Deleted Bob",
            normalized_name="alice" if name_id == 1 else "deleted bob",
            note="primary" if name_id == 1 else None,
            icon_path=None,
            deleted_at=None if name_id == 1 else "2026-01-01T00:00:00Z",
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-02T00:00:00Z",
            public_id=f"name-public-id-{name_id}",
        )

    def list_related_rows(
        self,
        name_id: int,
        role: str = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[RelatedRow]:
        _ = (role, include_deleted)
        if name_id != 1:
            return []
        return [
            RelatedRow(
                link_id=100,
                name_id=1,
                subtitle_id=20,
                title_id=10,
                relation_type="primary",
                subtitle_code="S-001",
                subtitle_name="Subtitle A",
                title_name="Title A",
                link_deleted_at=None,
                link_public_id="link-public-id-100",
                name_public_id="name-public-id-1",
                subtitle_public_id="subtitle-public-id-20",
                title_public_id="title-public-id-10",
            )
        ]


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_rich_search_tab_shows_result_and_selection_summaries() -> None:
    _app()
    tab = SearchTab(
        query_service=StubSearchQueryService(),
        role_context=RoleContext(role="admin", operator_id="op-1"),
    )

    summary = tab.summary_label.text()
    assert "検索結果 2件" in summary
    assert "表示中 2件" in summary
    assert "選択中 1件" in summary
    assert "関連 2件" in summary
    assert "有効 1件" in summary
    assert "削除済み 1件" in summary

    selection = tab.selection_summary_label.text()
    assert "選択中の名前: Alice" in selection
    assert "公開ID: name-public-id-1" in selection
    assert "関連合計 2件" in selection


def test_rich_search_tab_updates_summary_when_selection_changes() -> None:
    _app()
    tab = SearchTab(
        query_service=StubSearchQueryService(),
        role_context=RoleContext(role="admin", operator_id="op-1"),
    )

    tab.results_table.selectRow(1)

    selection = tab.selection_summary_label.text()
    assert "選択中の名前: Deleted Bob" in selection
    assert "関連合計 0件" in selection


def test_rich_search_tab_counts_multiple_selected_rows() -> None:
    _app()
    tab = SearchTab(
        query_service=StubSearchQueryService(),
        role_context=RoleContext(role="admin", operator_id="op-1"),
    )

    tab.results_table.clearSelection()
    tab.results_table.selectRow(0)
    selection_model = tab.results_table.selectionModel()
    assert selection_model is not None
    selection_model.select(
        tab.results_table.model().index(1, 0),
        QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows,
    )
    tab._update_rich_search_summaries()

    assert "選択中 2件" in tab.summary_label.text()

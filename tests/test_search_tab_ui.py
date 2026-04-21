"""UI tests for SearchTab."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.application.read_models import NameDetail, NameSearchRow, RelatedRow  # noqa: E402
from app.ui.search_tab import SearchTab  # noqa: E402


class StubQueryService:
    def search_names(
        self,
        query: str | None = None,
        role: str = "admin",
        *,
        exact_match: bool = False,
        title_id: int | None = None,
        has_links: bool | None = None,
        include_deleted: bool = False,
    ) -> list[NameSearchRow]:
        _ = (query, role, exact_match, title_id, has_links, include_deleted)
        return [
            NameSearchRow(
                id=1,
                raw_name="Alice",
                normalized_name="alice",
                note=None,
                deleted_at=None,
                linked_count=1,
                title_ids=(1,),
            )
        ]

    def get_name_detail(self, name_id: int, role: str = "admin") -> NameDetail:
        _ = (name_id, role)
        return NameDetail(
            id=1,
            raw_name="Alice",
            normalized_name="alice",
            note=None,
            icon_path=None,
            deleted_at=None,
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )

    def list_related_rows(
        self, name_id: int, role: str = "admin", *, include_deleted: bool = False
    ) -> list[RelatedRow]:
        _ = (name_id, role, include_deleted)
        return [
            RelatedRow(
                link_id=1,
                name_id=1,
                subtitle_id=1,
                title_id=1,
                relation_type="primary",
                subtitle_code="S1",
                subtitle_name="Subtitle",
                title_name="Title",
                link_deleted_at=None,
            )
        ]


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_search_tab_instantiation_and_render() -> None:
    _get_app()
    tab = SearchTab(query_service=StubQueryService())

    tab._on_search_clicked()

    assert tab.results_table.rowCount() == 1
    assert "Alice" in tab.detail_text.toPlainText()
    assert tab.related_table.rowCount() == 1

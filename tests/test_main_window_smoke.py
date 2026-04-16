"""Smoke tests for main window composition."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui.main_window import MainWindow  # noqa: E402


class EmptyQueryService:
    def search_names(self, *args: object, **kwargs: object) -> list[object]:
        _ = (args, kwargs)
        return []

    def get_name_detail(self, name_id: int) -> object:
        raise RuntimeError(f"not used: {name_id}")

    def list_related_rows(self, name_id: int, *, include_deleted: bool = False) -> list[object]:
        _ = (name_id, include_deleted)
        return []


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_main_window_has_search_tab() -> None:
    _get_app()
    window = MainWindow(query_service=EmptyQueryService())
    tab_widget = window.centralWidget()
    assert tab_widget is not None
    assert tab_widget.count() == 1
    assert tab_widget.tabText(0) == "検索/照合"

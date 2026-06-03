"""Regression coverage for subtitle management summary cards."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from tests.test_subtitle_management_tab_ui import _subtitle_tab  # noqa: E402


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_subtitle_target_cards_track_parent_and_selected_subtitle() -> None:
    _app()
    tab = _subtitle_tab()

    tab.editor.workflow_tabs.setCurrentWidget(tab.editor.edit_tab)
    tab.editor.titles_table.selectRow(0)
    tab.editor.subtitles_table.selectRow(0)

    assert tab.editor.property("parent_title_summary_split") is True
    assert tab.editor.property("selected_subtitle_summary_split") is True
    assert tab.parent_summary_edit.property("parent_title_summary_card") is True
    assert tab.subtitle_summary_edit.property("selected_subtitle_summary_card") is True
    assert "親タイトル" in tab.parent_summary_edit.text()
    assert "Alpha Title" in tab.parent_summary_edit.text()
    assert "選択中サブタイトル" in tab.subtitle_summary_edit.text()
    assert "S1" in tab.subtitle_summary_edit.text()
    assert "Alpha Subtitle" in tab.subtitle_summary_edit.text()


def test_subtitle_list_summary_remains_visible_after_search() -> None:
    _app()
    tab = _subtitle_tab()

    tab.subtitle_list_search_input.setText("beta")

    assert tab.subtitle_list_table.rowCount() == 2
    assert "一覧 3件" in tab.subtitle_list_summary_label.text()
    assert "表示中 2件" in tab.subtitle_list_summary_label.text()
    assert "親タイトル 1件" in tab.subtitle_list_summary_label.text()

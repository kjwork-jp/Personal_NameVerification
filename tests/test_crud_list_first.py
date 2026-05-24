"""Tests for CRUD list-first layout helper."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication
QLabel = qt_widgets.QLabel
QTableWidget = qt_widgets.QTableWidget
QVBoxLayout = qt_widgets.QVBoxLayout
QWidget = qt_widgets.QWidget

from app.ui.crud_list_first import apply_crud_list_first  # noqa: E402


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _hint_texts(widget: QWidget) -> list[str]:
    return [child.text() for child in widget.findChildren(QLabel, "listFirstWorkflowHint")]


def test_name_tab_table_is_moved_before_form_and_hint_added() -> None:
    _app()
    widget = QWidget()
    layout = QVBoxLayout(widget)
    header = QLabel("header")
    form = QLabel("form")
    table = QTableWidget(0, 1)
    widget.names_table = table
    layout.addWidget(header)
    layout.addWidget(form)
    layout.addWidget(table)

    apply_crud_list_first(widget, "名前を管理")

    assert widget.property("has_list_first_layout") is True
    assert widget.property("has_list_first_hint") is True
    assert layout.indexOf(table) == 1
    assert "一覧から名前を選択" in _hint_texts(widget)[0]


def test_title_subtitle_unified_tab_applies_child_editor_tables_and_hints() -> None:
    _app()
    unified = QWidget()
    unified_layout = QVBoxLayout(unified)
    unified_layout.addWidget(QLabel("header"))

    title_tab = QWidget()
    title_layout = QVBoxLayout(title_tab)
    title_layout.addWidget(QLabel("title header"))
    title_editor = QWidget()
    title_panel = QWidget()
    title_panel_layout = QVBoxLayout(title_panel)
    title_panel_layout.addWidget(QLabel("panel title"))
    title_form = QLabel("title form")
    titles_table = QTableWidget(0, 1)
    title_panel_layout.addWidget(title_form)
    title_panel_layout.addWidget(titles_table)
    title_editor.title_panel = title_panel
    title_editor.titles_table = titles_table
    title_tab.editor = title_editor

    subtitle_tab = QWidget()
    subtitle_layout = QVBoxLayout(subtitle_tab)
    subtitle_layout.addWidget(QLabel("subtitle header"))
    subtitle_editor = QWidget()
    subtitle_panel = QWidget()
    subtitle_panel_layout = QVBoxLayout(subtitle_panel)
    subtitle_panel_layout.addWidget(QLabel("panel subtitle"))
    subtitle_form = QLabel("subtitle form")
    subtitles_table = QTableWidget(0, 1)
    subtitle_panel_layout.addWidget(subtitle_form)
    subtitle_panel_layout.addWidget(subtitles_table)
    subtitle_editor.subtitle_panel = subtitle_panel
    subtitle_editor.subtitles_table = subtitles_table
    subtitle_tab.editor = subtitle_editor

    unified.title_tab = title_tab
    unified.subtitle_tab = subtitle_tab

    apply_crud_list_first(unified, "タイトル/サブタイトル管理")

    assert unified.property("has_list_first_layout") is True
    assert "一覧からタイトルまたはサブタイトル" in _hint_texts(unified)[0]
    assert title_tab.property("has_list_first_hint") is True
    assert subtitle_tab.property("has_list_first_hint") is True
    assert title_panel_layout.indexOf(titles_table) == 1
    assert subtitle_panel_layout.indexOf(subtitles_table) == 1


def test_relationship_tab_is_marked_and_gets_guidance() -> None:
    _app()
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("header"))

    apply_crud_list_first(widget, "関連付け")

    assert widget.property("has_list_first_layout") is True
    assert widget.property("relationship_workflow_guided") is True
    assert "登録/解除対象を上から順に選択" in _hint_texts(widget)[0]


def test_crud_list_first_is_idempotent() -> None:
    _app()
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("header"))
    table = QTableWidget(0, 1)
    widget.names_table = table
    layout.addWidget(table)

    apply_crud_list_first(widget, "名前を管理")
    first_hint_count = len(_hint_texts(widget))
    apply_crud_list_first(widget, "名前を管理")

    assert len(_hint_texts(widget)) == first_hint_count

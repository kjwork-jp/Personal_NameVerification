"""Tests for semantic workflow color accents."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui.subtitle_management_tab import SubtitleManagementTab  # noqa: E402
from app.ui.title_management_tab import TitleManagementTab  # noqa: E402
from tests.test_main_window_smoke import (  # noqa: E402
    EmptyCoreService,
    EmptyQueryService,
)


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_title_management_uses_workflow_color_accents() -> None:
    _get_app()
    tab = TitleManagementTab(
        core_service=EmptyCoreService(),
        query_service=EmptyQueryService(),
    )

    editor = tab.editor
    assert tab.property("workflow_accented_layout") is True
    assert editor.property("workflow_accented_layout") is True
    assert editor.workflow_hint_label.property("workflowAccent") == "guide"
    assert editor.title_panel_label.property("workflowAccent") == "list"
    assert editor.title_list_hint_label.property("workflowAccent") == "list"
    assert editor.title_refresh_button.property("workflowAccent") == "list"
    assert editor.title_create_button.property("workflowAccent") == "add"
    assert editor.title_update_button.property("workflowAccent") == "edit"
    assert editor.title_delete_button.property("workflowAccent") == "delete"
    assert editor.title_restore_button.property("workflowAccent") == "delete"
    assert editor.title_hard_delete_button.property("workflowAccent") == "delete"
    assert editor.title_detail_group.property("workflowAccent") == "edit"


def test_subtitle_management_uses_workflow_color_accents() -> None:
    _get_app()
    tab = SubtitleManagementTab(
        core_service=EmptyCoreService(),
        query_service=EmptyQueryService(),
    )

    editor = tab.editor
    assert tab.property("workflow_accented_layout") is True
    assert editor.property("workflow_accented_layout") is True
    assert editor.workflow_hint_label.property("workflowAccent") == "guide"
    assert editor.title_panel_label.property("workflowAccent") == "list"
    assert editor.title_list_hint_label.property("workflowAccent") == "list"
    assert editor.title_refresh_button.property("workflowAccent") == "list"
    assert editor.subtitle_refresh_button.property("workflowAccent") == "list"
    assert editor.subtitle_create_button.property("workflowAccent") == "add"
    assert editor.subtitle_update_button.property("workflowAccent") == "edit"
    assert editor.subtitle_delete_button.property("workflowAccent") == "delete"
    assert editor.subtitle_restore_button.property("workflowAccent") == "delete"
    assert editor.subtitle_hard_delete_button.property("workflowAccent") == "delete"
    assert editor.subtitle_group.property("workflowAccent") == "edit"
    assert editor.subtitle_panel_label.property("workflowAccent") == "edit"
    assert editor.subtitle_hint_label.property("workflowAccent") == "edit"

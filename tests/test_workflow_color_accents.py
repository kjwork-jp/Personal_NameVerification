"""Tests for semantic workflow color accents."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication
QGroupBox = qt_widgets.QGroupBox

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


def _groups_by_title(tab: object) -> dict[str, QGroupBox]:
    return {group.title(): group for group in tab.editor.findChildren(QGroupBox)}


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
    groups = _groups_by_title(tab)
    assert groups["タイトル削除"].property("workflowAccent") == "delete"
    assert groups["タイトル削除"].property("danger_operation_group") is True


def test_title_management_hides_subtitle_only_workflows() -> None:
    _get_app()
    tab = TitleManagementTab(
        core_service=EmptyCoreService(),
        query_service=EmptyQueryService(),
    )

    editor = tab.editor
    assert tab.property("focused_title_only_layout") is True
    assert editor.property("subtitle_controls_hidden_for_title_focus") is True
    assert editor.add_subtitle_title_combo.isHidden()
    assert editor.add_subtitle_name_input.isHidden()
    assert editor.subtitle_create_button.isHidden()
    assert editor.subtitle_update_button.isHidden()
    assert editor.subtitle_delete_button.isHidden()
    assert editor.subtitles_table.isHidden()
    groups = _groups_by_title(tab)
    assert groups["サブタイトルを新規追加"].isHidden()
    assert groups["サブタイトルを編集"].isHidden()
    assert groups["サブタイトル削除"].isHidden()
    assert groups["サブタイトル削除"].property("hiddenByFocusedTitleWrapper") is True


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
    groups = _groups_by_title(tab)
    assert groups["サブタイトル削除"].property("workflowAccent") == "delete"
    assert groups["サブタイトル削除"].property("danger_operation_group") is True


def test_subtitle_management_hides_title_mutation_workflows() -> None:
    _get_app()
    tab = SubtitleManagementTab(
        core_service=EmptyCoreService(),
        query_service=EmptyQueryService(),
    )

    editor = tab.editor
    assert tab.property("focused_subtitle_only_layout") is True
    assert editor.property("title_controls_hidden_for_subtitle_focus") is True
    assert editor.add_title_name_input.isHidden()
    assert editor.add_title_note_input.isHidden()
    assert editor.title_create_button.isHidden()
    assert editor.title_update_button.isHidden()
    assert editor.title_delete_button.isHidden()
    assert editor.delete_title_selector_combo.isHidden()
    groups = _groups_by_title(tab)
    assert groups["タイトルを新規追加"].isHidden()
    assert groups["タイトルを編集"].isHidden()
    assert groups["タイトル削除"].isHidden()
    assert groups["タイトル削除"].property("hiddenByFocusedSubtitleWrapper") is True

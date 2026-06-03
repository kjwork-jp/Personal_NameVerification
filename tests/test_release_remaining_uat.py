"""Remaining release UAT coverage for IDs, CRUD visibility, trash, logs, and guides."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
qt_core = pytest.importorskip("PySide6.QtCore", exc_type=ImportError)
QLabel = qt_widgets.QLabel
Qt = qt_core.Qt

from app.ui.audit_logs_tab import AuditLogsTab  # noqa: E402
from app.ui.subtitle_management_tab import SubtitleManagementTab  # noqa: E402
from app.ui.title_management_tab import TitleManagementTab  # noqa: E402
from tests.test_release_uat_coverage import _window_for_role  # noqa: E402

SEARCH_TAB = "検索"
NAME_TAB = "名前を管理"
TITLE_TAB = "タイトル管理"
SUBTITLE_TAB = "サブタイトル管理"
LINK_TAB = "関連付け"
TRASH_TAB = "削除データ"
AUDIT_TAB = "監査ログ"
OPERATIONS_TAB = "データ入出力"

EXPECTED_REGISTER_NAME = "Alice"
EXPECTED_REGISTER_TITLE = "Title1"
EXPECTED_UNREGISTER_LINK = "Title1 / S1 / Sub1"
READONLY_TEXT = "参照のみ"
CHANGE_LOG_TEXT = "データ変更ログ"
USER_AUTH_LOG_TEXT = "ユーザー/認証ログ"
AUDIT_GUIDE_TEXT = "ガイド"
ADMIN_GUIDE_TITLE = "操作ガイド（admin）"
ADMIN_GUIDE_DETAIL = "データ入出力の全操作"


def _assert_full_public_id(text: str, expected: str) -> None:
    assert text == expected
    assert "..." not in text
    assert "…" not in text


def test_remaining_uat_public_ids_are_full_across_primary_tables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = _window_for_role("admin", monkeypatch)

    search_tab = window._tabs_by_name[SEARCH_TAB]
    _assert_full_public_id(search_tab.results_table.item(0, 1).text(), "name-public-id-001")
    search_tab.results_table.selectRow(0)
    search_tab._on_selection_changed()
    _assert_full_public_id(search_tab.related_table.item(0, 1).text(), "link-public-id-001")

    name_tab = window._tabs_by_name[NAME_TAB]
    _assert_full_public_id(name_tab.names_table.item(0, 1).text(), "name-public-id-001")

    title_tab = window._tabs_by_name[TITLE_TAB]
    assert isinstance(title_tab, TitleManagementTab)
    title_editor = title_tab.editor
    _assert_full_public_id(title_editor.titles_table.item(0, 1).text(), "title-public-id-001")

    subtitle_tab = window._tabs_by_name[SUBTITLE_TAB]
    assert isinstance(subtitle_tab, SubtitleManagementTab)
    subtitle_editor = subtitle_tab.editor
    subtitle_editor.titles_table.selectRow(0)
    subtitle_editor._on_title_selected()
    _assert_full_public_id(
        subtitle_editor.subtitles_table.item(0, 1).text(),
        "subtitle-public-id-001",
    )

    link_tab = window._tabs_by_name[LINK_TAB]
    assert link_tab.register_name_combo.itemText(0) == EXPECTED_REGISTER_NAME
    assert link_tab.register_title_combo.itemText(0) == EXPECTED_REGISTER_TITLE
    assert link_tab.unregister_link_combo.itemText(0) == EXPECTED_UNREGISTER_LINK
    name_tooltip = link_tab.register_name_combo.itemData(0, Qt.ItemDataRole.ToolTipRole)
    title_tooltip = link_tab.register_title_combo.itemData(0, Qt.ItemDataRole.ToolTipRole)
    link_tooltip = link_tab.unregister_link_combo.itemData(0, Qt.ItemDataRole.ToolTipRole)
    _assert_full_public_id(
        name_tooltip.split("公開ID: ")[1].split("\n")[0],
        "name-public-id-001",
    )
    _assert_full_public_id(
        title_tooltip.split("公開ID: ")[1].split("\n")[0],
        "title-public-id-001",
    )
    _assert_full_public_id(
        link_tooltip.split("リンク公開ID: ")[1].split("\n")[0],
        "link-public-id-001",
    )


def test_remaining_uat_crud_and_delete_controls_follow_role_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    viewer = _window_for_role("viewer", monkeypatch)
    editor = _window_for_role("editor", monkeypatch)
    admin = _window_for_role("admin", monkeypatch)

    viewer_name = viewer._tabs_by_name[NAME_TAB]
    editor_name = editor._tabs_by_name[NAME_TAB]
    admin_name = admin._tabs_by_name[NAME_TAB]
    assert viewer_name.create_button.isHidden()
    assert viewer_name.update_button.isHidden()
    assert viewer_name.delete_button.isHidden()
    assert not editor_name.create_button.isHidden()
    assert not editor_name.update_button.isHidden()
    assert editor_name.delete_button.isHidden()
    assert not admin_name.delete_button.isHidden()

    viewer_title = viewer._tabs_by_name[TITLE_TAB]
    editor_title = editor._tabs_by_name[TITLE_TAB]
    admin_title = admin._tabs_by_name[TITLE_TAB]
    viewer_subtitle = viewer._tabs_by_name[SUBTITLE_TAB]
    editor_subtitle = editor._tabs_by_name[SUBTITLE_TAB]
    admin_subtitle = admin._tabs_by_name[SUBTITLE_TAB]
    assert isinstance(viewer_title, TitleManagementTab)
    assert isinstance(editor_title, TitleManagementTab)
    assert isinstance(admin_title, TitleManagementTab)
    assert isinstance(viewer_subtitle, SubtitleManagementTab)
    assert isinstance(editor_subtitle, SubtitleManagementTab)
    assert isinstance(admin_subtitle, SubtitleManagementTab)

    viewer_title_editor = viewer_title.editor
    editor_title_editor = editor_title.editor
    admin_title_editor = admin_title.editor
    viewer_subtitle_editor = viewer_subtitle.editor
    editor_subtitle_editor = editor_subtitle.editor
    admin_subtitle_editor = admin_subtitle.editor
    assert viewer_title_editor.title_create_button.isHidden()
    assert viewer_title_editor.title_update_button.isHidden()
    assert viewer_subtitle_editor.subtitle_create_button.isHidden()
    assert viewer_subtitle_editor.subtitle_update_button.isHidden()
    assert not editor_title_editor.title_create_button.isHidden()
    assert not editor_title_editor.title_update_button.isHidden()
    assert editor_title_editor.title_delete_button.isHidden()
    assert not editor_subtitle_editor.subtitle_create_button.isHidden()
    assert not editor_subtitle_editor.subtitle_update_button.isHidden()
    assert editor_subtitle_editor.subtitle_delete_button.isHidden()
    assert not admin_title_editor.title_delete_button.isHidden()
    assert not admin_subtitle_editor.subtitle_delete_button.isHidden()


def test_remaining_uat_audit_and_operations_labels(monkeypatch: pytest.MonkeyPatch) -> None:
    admin = _window_for_role("admin", monkeypatch)
    audit = admin._tabs_by_name[AUDIT_TAB]
    operations = admin._tabs_by_name[OPERATIONS_TAB]

    assert isinstance(audit, AuditLogsTab)
    audit_tab_labels = [audit.tabs.tabText(index) for index in range(audit.tabs.count())]
    assert CHANGE_LOG_TEXT in audit_tab_labels
    assert AUDIT_GUIDE_TEXT in audit_tab_labels
    if audit.user_audit_tab is not None:
        assert USER_AUTH_LOG_TEXT in audit_tab_labels

    labels = operations.findChildren(QLabel)
    label_texts = [label.text() for label in labels]
    assert any(ADMIN_GUIDE_TITLE in text for text in label_texts)
    assert any(ADMIN_GUIDE_DETAIL in text for text in label_texts)

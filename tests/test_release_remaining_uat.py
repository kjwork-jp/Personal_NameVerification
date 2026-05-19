"""Remaining release UAT coverage for IDs, CRUD visibility, trash, logs, and guides."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QLabel = qt_widgets.QLabel

from app.ui.audit_logs_tab import AuditLogsTab  # noqa: E402
from app.ui.title_subtitle_unified_tab import TitleSubtitleUnifiedTab  # noqa: E402
from tests.test_release_uat_coverage import _window_for_role  # noqa: E402

SEARCH_TAB = "\u691c\u7d22"
NAME_TAB = "\u540d\u524d\u3092\u7ba1\u7406"
TITLE_SUBTITLE_TAB = (
    "\u30bf\u30a4\u30c8\u30eb/"
    "\u30b5\u30d6\u30bf\u30a4\u30c8\u30eb\u7ba1\u7406"
)
LINK_TAB = "\u95a2\u9023\u4ed8\u3051"
TRASH_TAB = "\u524a\u9664\u30c7\u30fc\u30bf"
AUDIT_TAB = "\u76e3\u67fb\u30ed\u30b0"
OPERATIONS_TAB = "\u30c7\u30fc\u30bf\u5165\u51fa\u529b"

EXPECTED_REGISTER_NAME = (
    "\u540d\u524d: Alice"
    "\uff08\u516c\u958bID: name-public-id-001\uff09"
)
EXPECTED_REGISTER_TITLE = (
    "\u30bf\u30a4\u30c8\u30eb: Title1"
    "\uff08\u516c\u958bID: title-public-id-001\uff09"
)
EXPECTED_UNREGISTER_LINK = (
    "Title1 > S1: Sub1"
    "\uff08\u30ea\u30f3\u30afID: link-public-id-001\uff09"
)
READONLY_TEXT = "\u53c2\u7167\u306e\u307f"
CHANGE_LOG_TEXT = "\u30c7\u30fc\u30bf\u5909\u66f4\u30ed\u30b0"
USER_AUTH_LOG_TEXT = "\u30e6\u30fc\u30b6\u30fc/\u8a8d\u8a3c\u30ed\u30b0"
ADMIN_GUIDE_TITLE = "\u64cd\u4f5c\u30ac\u30a4\u30c9\uff08admin\uff09"
ADMIN_GUIDE_DETAIL = "\u30c7\u30fc\u30bf\u5165\u51fa\u529b\u306e\u5168\u64cd\u4f5c"


def _assert_full_public_id(text: str, expected: str) -> None:
    assert text == expected
    assert "..." not in text
    assert "\u2026" not in text


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

    title_unified = window._tabs_by_name[TITLE_SUBTITLE_TAB]
    assert isinstance(title_unified, TitleSubtitleUnifiedTab)
    title_editor = title_unified.title_tab.editor
    _assert_full_public_id(title_editor.titles_table.item(0, 1).text(), "title-public-id-001")
    _assert_full_public_id(
        title_editor.subtitles_table.item(0, 1).text(),
        "subtitle-public-id-001",
    )

    link_tab = window._tabs_by_name[LINK_TAB]
    assert link_tab.register_name_combo.itemText(0) == EXPECTED_REGISTER_NAME
    assert link_tab.register_title_combo.itemText(0) == EXPECTED_REGISTER_TITLE
    assert link_tab.unregister_link_combo.itemText(0) == EXPECTED_UNREGISTER_LINK


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

    viewer_title = viewer._tabs_by_name[TITLE_SUBTITLE_TAB]
    editor_title = editor._tabs_by_name[TITLE_SUBTITLE_TAB]
    admin_title = admin._tabs_by_name[TITLE_SUBTITLE_TAB]
    assert isinstance(viewer_title, TitleSubtitleUnifiedTab)
    assert isinstance(editor_title, TitleSubtitleUnifiedTab)
    assert isinstance(admin_title, TitleSubtitleUnifiedTab)

    viewer_editor = viewer_title.title_tab.editor
    editor_editor = editor_title.title_tab.editor
    admin_editor = admin_title.title_tab.editor
    assert viewer_editor.title_create_button.isHidden()
    assert viewer_editor.title_update_button.isHidden()
    assert viewer_editor.subtitle_create_button.isHidden()
    assert viewer_editor.subtitle_update_button.isHidden()
    assert not editor_editor.title_create_button.isHidden()
    assert not editor_editor.subtitle_create_button.isHidden()
    assert editor_editor.title_delete_button.isHidden()
    assert editor_editor.subtitle_delete_button.isHidden()
    assert not admin_editor.title_delete_button.isHidden()
    assert not admin_editor.subtitle_delete_button.isHidden()


def test_remaining_uat_trash_controls_are_admin_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    viewer = _window_for_role("viewer", monkeypatch)
    editor = _window_for_role("editor", monkeypatch)
    admin = _window_for_role("admin", monkeypatch)

    viewer_trash = viewer._tabs_by_name[TRASH_TAB]
    editor_trash = editor._tabs_by_name[TRASH_TAB]
    admin_trash = admin._tabs_by_name[TRASH_TAB]

    assert viewer_trash.operator_input.isHidden()
    assert viewer_trash.restore_button.isHidden()
    assert viewer_trash.hard_delete_button.isHidden()
    assert READONLY_TEXT in viewer_trash.message_label.text()

    assert editor_trash.operator_input.isHidden()
    assert editor_trash.restore_button.isHidden()
    assert editor_trash.hard_delete_button.isHidden()
    assert READONLY_TEXT in editor_trash.message_label.text()

    assert not admin_trash.operator_input.isHidden()
    assert not admin_trash.restore_button.isHidden()
    assert not admin_trash.hard_delete_button.isHidden()


def test_remaining_uat_log_meaning_and_guide_wording(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = _window_for_role("admin", monkeypatch)
    audit_tab = window._tabs_by_name[AUDIT_TAB]
    assert isinstance(audit_tab, AuditLogsTab)

    data_log = audit_tab.data_change_tab
    _assert_full_public_id(data_log.logs_table.item(0, 1).text(), "change-public-id-001")
    assert "\u516c\u958bID: change-public-id-001" in data_log.detail_summary_label.text()
    assert "raw_name: Alice \u2192 Alice Updated" in data_log.diff_view.toPlainText()

    labels_text = "\n".join(label.text() for label in audit_tab.findChildren(QLabel))
    assert CHANGE_LOG_TEXT in labels_text
    assert USER_AUTH_LOG_TEXT in labels_text
    assert "Operations Log" in labels_text

    operations = window._tabs_by_name[OPERATIONS_TAB]
    guide_label = operations.findChild(QLabel, "operationsRoleGuideLabel")
    assert guide_label is not None
    assert ADMIN_GUIDE_TITLE in guide_label.text()
    assert ADMIN_GUIDE_DETAIL in guide_label.text()

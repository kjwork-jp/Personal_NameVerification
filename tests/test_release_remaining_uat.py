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


def _assert_full_public_id(text: str, expected: str) -> None:
    assert text == expected
    assert "..." not in text
    assert "…" not in text


def test_remaining_uat_public_ids_are_full_across_primary_tables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = _window_for_role("admin", monkeypatch)

    search_tab = window._tabs_by_name["検索"]
    _assert_full_public_id(search_tab.results_table.item(0, 1).text(), "name-public-id-001")
    search_tab.results_table.selectRow(0)
    search_tab._on_selection_changed()
    _assert_full_public_id(search_tab.related_table.item(0, 1).text(), "link-public-id-001")

    name_tab = window._tabs_by_name["名前を管理"]
    _assert_full_public_id(name_tab.names_table.item(0, 1).text(), "name-public-id-001")

    title_unified = window._tabs_by_name["タイトル/サブタイトル管理"]
    assert isinstance(title_unified, TitleSubtitleUnifiedTab)
    title_editor = title_unified.title_tab.editor
    _assert_full_public_id(title_editor.titles_table.item(0, 1).text(), "title-public-id-001")
    _assert_full_public_id(
        title_editor.subtitles_table.item(0, 1).text(),
        "subtitle-public-id-001",
    )

    link_tab = window._tabs_by_name["関連付け"]
    assert link_tab.register_name_combo.itemText(0) == "名前: Alice（公開ID: name-public-id-001）"
    assert link_tab.register_title_combo.itemText(0) == "タイトル: Title1（公開ID: title-public-id-001）"
    assert link_tab.unregister_link_combo.itemText(0) == (
        "Title1 > S1: Sub1（リンクID: link-public-id-001）"
    )


def test_remaining_uat_crud_and_delete_controls_follow_role_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    viewer = _window_for_role("viewer", monkeypatch)
    editor = _window_for_role("editor", monkeypatch)
    admin = _window_for_role("admin", monkeypatch)

    viewer_name = viewer._tabs_by_name["名前を管理"]
    editor_name = editor._tabs_by_name["名前を管理"]
    admin_name = admin._tabs_by_name["名前を管理"]
    assert viewer_name.create_button.isHidden()
    assert viewer_name.update_button.isHidden()
    assert viewer_name.delete_button.isHidden()
    assert not editor_name.create_button.isHidden()
    assert not editor_name.update_button.isHidden()
    assert editor_name.delete_button.isHidden()
    assert not admin_name.delete_button.isHidden()

    viewer_title = viewer._tabs_by_name["タイトル/サブタイトル管理"]
    editor_title = editor._tabs_by_name["タイトル/サブタイトル管理"]
    admin_title = admin._tabs_by_name["タイトル/サブタイトル管理"]
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

    viewer_trash = viewer._tabs_by_name["削除データ"]
    editor_trash = editor._tabs_by_name["削除データ"]
    admin_trash = admin._tabs_by_name["削除データ"]

    assert viewer_trash.operator_input.isHidden()
    assert viewer_trash.restore_button.isHidden()
    assert viewer_trash.hard_delete_button.isHidden()
    assert "参照のみ" in viewer_trash.message_label.text()

    assert editor_trash.operator_input.isHidden()
    assert editor_trash.restore_button.isHidden()
    assert editor_trash.hard_delete_button.isHidden()
    assert "参照のみ" in editor_trash.message_label.text()

    assert not admin_trash.operator_input.isHidden()
    assert not admin_trash.restore_button.isHidden()
    assert not admin_trash.hard_delete_button.isHidden()


def test_remaining_uat_log_meaning_and_guide_wording(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = _window_for_role("admin", monkeypatch)
    audit_tab = window._tabs_by_name["監査ログ"]
    assert isinstance(audit_tab, AuditLogsTab)

    data_log = audit_tab.data_change_tab
    _assert_full_public_id(data_log.logs_table.item(0, 1).text(), "change-public-id-001")
    assert "公開ID: change-public-id-001" in data_log.detail_summary_label.text()
    assert "raw_name: Alice → Alice Updated" in data_log.diff_view.toPlainText()

    labels_text = "\n".join(label.text() for label in audit_tab.findChildren(QLabel))
    assert "データ変更ログ" in labels_text
    assert "ユーザー/認証ログ" in labels_text
    assert "Operations Log" in labels_text

    operations = window._tabs_by_name["データ入出力"]
    guide_label = operations.findChild(QLabel, "operationsRoleGuideLabel")
    assert guide_label is not None
    assert "操作ガイド（admin）" in guide_label.text()
    assert "データ入出力の全操作" in guide_label.text()

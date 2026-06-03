"""UI tests for the focused title management tab."""

from __future__ import annotations

import os

import pytest

from app.application.read_models import NameSearchRow, NameTitleLinkRow, SubtitleDetail, TitleDetail

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui.role_context import RoleContext  # noqa: E402
from app.ui.title_management_tab import TitleManagementTab  # noqa: E402


class StubCoreService:
    pass


class StubQueryService:
    def __init__(self) -> None:
        self.titles = [
            TitleDetail(
                id=1,
                title_name="Title1",
                note=None,
                icon_path=None,
                deleted_at=None,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            ),
            TitleDetail(
                id=2,
                title_name="Title2",
                note="memo",
                icon_path=None,
                deleted_at="2026-01-02T00:00:00Z",
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-02T00:00:00Z",
            ),
        ]

    def search_names(self, *args, **kwargs) -> list[NameSearchRow]:  # type: ignore[no-untyped-def]
        _ = (args, kwargs)
        return [
            NameSearchRow(
                id=100,
                raw_name="Alice",
                normalized_name="alice",
                note=None,
                deleted_at=None,
                linked_count=0,
                title_ids=(),
            )
        ]

    def list_names_for_title(
        self,
        title_id: int,
        role: str = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[NameTitleLinkRow]:
        _ = (role, include_deleted)
        if title_id != 1:
            return []
        return [
            NameTitleLinkRow(
                link_id=900,
                name_id=100,
                title_id=1,
                relation_type="primary",
                raw_name="Alice",
                title_name="Title1",
                link_deleted_at=None,
            )
        ]

    def list_titles(
        self,
        role: str = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[TitleDetail]:
        _ = (role, include_deleted)
        return self.titles

    def list_subtitles(
        self,
        title_id: int,
        role: str = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[SubtitleDetail]:
        _ = (title_id, role, include_deleted)
        return []


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _title_tab() -> TitleManagementTab:
    _app()
    return TitleManagementTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(),
        role_context=RoleContext(role="admin", operator_id="op-1"),
    )


def test_title_management_split_summary_and_danger_copy_properties() -> None:
    tab = _title_tab()

    tab.editor.workflow_tabs.setCurrentWidget(tab.editor.edit_tab)
    tab.editor.titles_table.selectRow(0)

    edit_summary = tab.editor.selected_title_context_label.text()
    assert tab.property("title_selection_redesigned") is True
    assert tab.editor.property("title_summary_split") is True
    assert tab.editor.property("title_edit_target_summary_card") is True
    assert tab.editor.selected_title_context_label.property("selected_title_summary_card") is True
    assert (
        tab.editor.selected_title_context_label.property("title_edit_target_summary_card")
        is True
    )
    assert "編集対象タイトル" in edit_summary
    assert "タイトル名  Title1" in edit_summary
    assert "内部ID      1" in edit_summary
    assert "状態        有効" in edit_summary
    assert "関連名      Alice" in edit_summary
    assert tab.editor.title_detail_group.title() == "タイトル編集: 選択カード確認後に更新"
    assert tab.editor.title_update_button.text() == "選択中タイトルを更新"

    tab.editor.workflow_tabs.setCurrentWidget(tab.editor.delete_tab)
    target_summary = tab.title_delete_target_summary.text()
    assert tab.title_delete_target_summary.property("title_delete_target_summary_card") is True
    assert "削除対象タイトル" in target_summary
    assert "タイトル名  Title1" in target_summary
    assert "内部ID      1" in target_summary
    assert "関連名      Alice" in target_summary
    assert tab.editor.property("title_delete_danger_copy") is True
    assert tab.editor.title_delete_button.text() == "選択中タイトルをゴミ箱に入れる"
    assert tab.editor.title_restore_button.text() == "選択中の削除済みタイトルを復元"
    assert tab.editor.title_hard_delete_button.text() == "選択中の削除済みタイトルを完全削除"


def test_title_list_summary_shows_totals_and_selection_count() -> None:
    tab = _title_tab()

    summary = tab.title_list_summary_label.text()
    assert tab.property("title_list_summary_counters") is True
    assert tab.editor.property("title_list_summary_counters") is True
    assert tab.title_list_summary_label.property("title_list_summary_counter") is True
    assert "一覧 2件" in summary
    assert "選択中 0件" in summary
    assert "有効 1件" in summary
    assert "削除済み 1件" in summary
    assert "関連名あり 1件" in summary

    tab.editor.titles_table.selectRow(0)

    assert "選択中 1件" in tab.title_list_summary_label.text()


def test_title_selection_cards_follow_combo_and_table_selection() -> None:
    tab = _title_tab()

    tab.editor.workflow_tabs.setCurrentWidget(tab.editor.edit_tab)
    tab.editor.title_selector_combo.setCurrentIndex(1)

    assert tab.editor.title_name_input.text() == "Title1"
    assert "編集対象タイトル" in tab.editor.selected_title_context_label.text()
    assert "内部ID      1" in tab.editor.selected_title_context_label.text()
    assert "削除対象タイトル" in tab.title_delete_target_summary.text()
    assert "内部ID      1" in tab.title_delete_target_summary.text()

    tab.editor.delete_title_selector_combo.setCurrentIndex(2)

    assert "削除対象タイトル" in tab.title_delete_target_summary.text()
    assert "タイトル名  Title2" in tab.title_delete_target_summary.text()
    assert "内部ID      2" in tab.title_delete_target_summary.text()
    assert "状態        削除済み" in tab.title_delete_target_summary.text()


def test_title_destructive_confirmation_includes_target_details() -> None:
    tab = _title_tab()
    tab.editor.workflow_tabs.setCurrentWidget(tab.editor.delete_tab)
    tab.editor.titles_table.selectRow(0)

    message = tab._title_destructive_confirmation_text(
        "ゴミ箱に入れる",
        tab._selected_title_detail(),
        1,
        "delete_title",
    )

    assert "対象タイトル: Title1" in message
    assert "内部ID: 1" in message
    assert "状態: 有効" in message
    assert "関連名: Alice" in message
    assert "通常の編集対象から外れます" in message

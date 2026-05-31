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


def test_title_management_split_summary_and_danger_copy_properties() -> None:
    _app()
    tab = TitleManagementTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(),
        role_context=RoleContext(role="admin", operator_id="op-1"),
    )

    tab.editor.workflow_tabs.setCurrentWidget(tab.editor.edit_tab)
    tab.editor.titles_table.selectRow(0)

    edit_summary = tab.editor.selected_title_context_label.text()
    assert tab.editor.property("title_summary_split") is True
    assert tab.editor.selected_title_context_label.property("selected_title_summary_card") is True
    assert "選択中タイトル" in edit_summary
    assert "タイトル名  Title1" in edit_summary
    assert "状態        有効" in edit_summary
    assert "関連名      Alice" in edit_summary

    tab.editor.workflow_tabs.setCurrentWidget(tab.editor.delete_tab)
    target_summary = tab.title_delete_target_summary.text()
    assert tab.title_delete_target_summary.property("title_delete_target_summary_card") is True
    assert "削除対象タイトル" in target_summary
    assert "タイトル名  Title1" in target_summary
    assert "関連名      Alice" in target_summary
    assert tab.editor.property("title_delete_danger_copy") is True
    assert tab.editor.title_delete_button.text() == "選択中タイトルをゴミ箱に入れる"
    assert tab.editor.title_restore_button.text() == "削除済みタイトルを復元"
    assert tab.editor.title_hard_delete_button.text() == "削除済みタイトルを完全削除"

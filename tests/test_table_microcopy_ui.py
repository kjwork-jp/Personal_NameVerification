"""UI tests for table readability and microcopy consistency."""

# ruff: noqa: E402, I001

from __future__ import annotations

import os

import pytest

from app.application.read_models import NameDetail, NameSearchRow

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui.name_management_tab import NameManagementTab
from app.ui.public_id_display import public_id_detail, short_public_id
from app.ui.role_context import RoleContext


LONG_PUBLIC_ID = "12345678-1234-1234-1234-123456789abc"
DELETED_PUBLIC_ID = "deleted-public-id"


class StubCoreService:
    pass


class StubQueryService:
    def search_names(self, *args, **kwargs) -> list[NameSearchRow]:  # type: ignore[no-untyped-def]
        _ = (args, kwargs)
        return [
            NameSearchRow(
                id=1,
                raw_name="Alice",
                normalized_name="alice",
                note="primary note",
                deleted_at=None,
                linked_count=3,
                title_ids=(10,),
                public_id=LONG_PUBLIC_ID,
                title_related_count=1,
                subtitle_related_count=2,
            ),
            NameSearchRow(
                id=2,
                raw_name="Deleted Bob",
                normalized_name="deleted bob",
                note="deleted note",
                deleted_at="2026-01-01T00:00:00Z",
                linked_count=4,
                title_ids=(11,),
                public_id=DELETED_PUBLIC_ID,
                title_related_count=3,
                subtitle_related_count=1,
            ),
        ]

    def get_name_detail(self, name_id: int, role: str = "admin") -> NameDetail:
        _ = role
        if name_id == 2:
            return NameDetail(
                id=2,
                raw_name="Deleted Bob",
                normalized_name="deleted bob",
                note="deleted note",
                icon_path=None,
                deleted_at="2026-01-01T00:00:00Z",
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
                public_id=DELETED_PUBLIC_ID,
            )
        return NameDetail(
            id=1,
            raw_name="Alice",
            normalized_name="alice",
            note="primary note",
            icon_path=None,
            deleted_at=None,
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
            public_id=LONG_PUBLIC_ID,
        )


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _name_tab() -> NameManagementTab:
    _app()
    return NameManagementTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(),
        role_context=RoleContext(role="admin", operator_id="op-1"),
    )


def test_public_id_table_display_keeps_full_detail() -> None:
    assert short_public_id(LONG_PUBLIC_ID) == LONG_PUBLIC_ID
    assert public_id_detail(LONG_PUBLIC_ID) == LONG_PUBLIC_ID
    assert short_public_id(None) == "未採番"
    assert public_id_detail(None) == "未採番"


def test_name_table_uses_short_public_id_with_full_tooltip() -> None:
    tab = _name_tab()

    public_id_item = tab.names_table.item(0, 1)
    assert public_id_item is not None
    assert public_id_item.text() == LONG_PUBLIC_ID
    assert public_id_item.toolTip() == f"公開ID: {LONG_PUBLIC_ID}"


def test_name_list_summary_shows_totals_and_selection_count() -> None:
    tab = _name_tab()

    summary = tab.list_summary_label.text()
    assert "一覧 2件" in summary
    assert "選択中 0件" in summary
    assert "有効 1件" in summary
    assert "削除済み 1件" in summary
    assert "タイトル関連 4件" in summary
    assert "サブタイトル関連 3件" in summary
    assert "関連合計 7件" in summary

    tab.names_table.selectRow(0)

    assert "選択中 1件" in tab.list_summary_label.text()

# ruff: noqa: I001
"""Tests for native workflow-tab layout in the name management tab."""

from __future__ import annotations

import os

import pytest

from app.application.read_models import NameDetail

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication
QLabel = qt_widgets.QLabel
QTableWidget = qt_widgets.QTableWidget

from app.application.read_models import NameSearchRow  # noqa: E402
from app.ui.crud_list_first import apply_crud_list_first  # noqa: E402
from app.ui.name_management_tab import NameManagementTab  # noqa: E402


class StubCoreService:
    def create_name(self, payload, operator_id: str, role: str = "admin") -> int:  # type: ignore[no-untyped-def]
        return 1

    def update_name(self, name_id: int, payload, operator_id: str, role: str = "admin") -> None:  # type: ignore[no-untyped-def]
        return None

    def delete_name(self, name_id: int, operator_id: str, role: str = "admin") -> None:
        return None

    def restore_name(self, name_id: int, operator_id: str, role: str = "admin") -> None:
        return None

    def hard_delete_name(self, name_id: int, operator_id: str, role: str = "admin") -> None:
        return None


class StubQueryService:
    def search_names(self, *args: object, **kwargs: object) -> list[NameSearchRow]:
        _ = args, kwargs
        return [
            NameSearchRow(
                id=1,
                raw_name="Alice",
                normalized_name="alice",
                note=None,
                deleted_at=None,
                linked_count=0,
                title_ids=(),
            )
        ]

    def get_name_detail(self, name_id: int, role: str = "admin") -> NameDetail:
        _ = role
        return NameDetail(
            id=name_id,
            raw_name="Alice",
            normalized_name="alice",
            note=None,
            icon_path=None,
            deleted_at=None,
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_name_management_tab_is_native_workflow_tabs() -> None:
    _app()
    tab = NameManagementTab(core_service=StubCoreService(), query_service=StubQueryService())
    layout = tab.layout()
    assert layout is not None

    hint_index = layout.indexOf(tab.workflow_hint_label)
    tabs_index = layout.indexOf(tab.workflow_tabs)

    assert tab.property("native_list_first_layout") is True
    assert tab.property("has_list_first_layout") is True
    assert tab.property("has_list_first_hint") is True
    assert tab.property("workflow_tabs_layout") is True
    assert tab.workflow_hint_label.objectName() == "nativeListFirstWorkflowHint"
    assert "新規追加は選択状態を持ち込みません" in tab.workflow_hint_label.text()
    assert hint_index < tabs_index
    assert [tab.workflow_tabs.tabText(index) for index in range(tab.workflow_tabs.count())] == [
        "一覧",
        "新規追加",
        "編集",
        "削除",
        "ガイド",
    ]


def test_crud_helper_skips_native_name_layout() -> None:
    _app()
    tab = NameManagementTab(core_service=StubCoreService(), query_service=StubQueryService())

    apply_crud_list_first(tab, "名前を管理")

    assert len(tab.findChildren(QTableWidget)) == 1
    assert len(tab.findChildren(QLabel, "nativeListFirstWorkflowHint")) >= 1
    assert not tab.findChildren(QLabel, "listFirstWorkflowHint")

# ruff: noqa: I001
"""Tests for native list-first layout in the name management tab."""

from __future__ import annotations

import os

import pytest

from app.application.read_models import NameDetail

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication
QFormLayout = qt_widgets.QFormLayout
QHBoxLayout = qt_widgets.QHBoxLayout
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


def test_name_management_tab_is_native_list_first() -> None:
    _app()
    tab = NameManagementTab(core_service=StubCoreService(), query_service=StubQueryService())
    layout = tab.layout()
    assert layout is not None

    table_index = layout.indexOf(tab.names_table)
    hint_index = layout.indexOf(tab.workflow_hint_label)
    form_index = -1
    actions_index = -1
    for index in range(layout.count()):
        item = layout.itemAt(index)
        child_layout = item.layout() if item is not None else None
        if isinstance(child_layout, QFormLayout):
            form_index = index
        if isinstance(child_layout, QHBoxLayout):
            actions_index = index

    assert tab.property("native_list_first_layout") is True
    assert tab.property("has_list_first_layout") is True
    assert tab.property("has_list_first_hint") is True
    assert tab.workflow_hint_label.objectName() == "nativeListFirstWorkflowHint"
    assert "一覧から名前を選択" in tab.workflow_hint_label.text()
    assert hint_index < table_index < form_index < actions_index


def test_crud_helper_skips_native_name_layout() -> None:
    _app()
    tab = NameManagementTab(core_service=StubCoreService(), query_service=StubQueryService())

    apply_crud_list_first(tab, "名前を管理")

    assert len(tab.findChildren(QTableWidget)) == 1
    assert len(tab.findChildren(QLabel, "nativeListFirstWorkflowHint")) == 1
    assert not tab.findChildren(QLabel, "listFirstWorkflowHint")

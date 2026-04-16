"""UI tests for NameManagementTab."""

from __future__ import annotations

import os

import pytest

from app.application.read_models import NameDetail, NameSearchRow

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui.name_management_tab import NameManagementTab  # noqa: E402


class StubCoreService:
    def __init__(self) -> None:
        self.called: list[str] = []

    def create_name(self, payload, operator_id: str) -> int:  # type: ignore[no-untyped-def]
        self.called.append(f"create:{payload.raw_name}:{operator_id}")
        return 1

    def update_name(self, name_id: int, payload, operator_id: str) -> None:  # type: ignore[no-untyped-def]
        self.called.append(f"update:{name_id}:{payload.raw_name}:{operator_id}")

    def delete_name(self, name_id: int, operator_id: str) -> None:
        self.called.append(f"delete:{name_id}:{operator_id}")

    def restore_name(self, name_id: int, operator_id: str) -> None:
        self.called.append(f"restore:{name_id}:{operator_id}")

    def hard_delete_name(self, name_id: int, operator_id: str) -> None:
        self.called.append(f"hard_delete:{name_id}:{operator_id}")


class StubQueryService:
    def __init__(self) -> None:
        self.rows = [
            NameSearchRow(
                id=1,
                raw_name="Alice",
                normalized_name="alice",
                note=None,
                deleted_at=None,
                linked_count=0,
                title_ids=(),
            ),
            NameSearchRow(
                id=2,
                raw_name="Bob",
                normalized_name="bob",
                note="memo",
                deleted_at="2026-01-01T00:00:00Z",
                linked_count=0,
                title_ids=(),
            ),
        ]

    def search_names(self, *args: object, **kwargs: object) -> list[NameSearchRow]:
        _ = (args, kwargs)
        return self.rows

    def get_name_detail(self, name_id: int) -> NameDetail:
        if name_id == 2:
            deleted_at = "2026-01-01T00:00:00Z"
            note = "memo"
            raw_name = "Bob"
            normalized = "bob"
        else:
            deleted_at = None
            note = None
            raw_name = "Alice"
            normalized = "alice"
        return NameDetail(
            id=name_id,
            raw_name=raw_name,
            normalized_name=normalized,
            note=note,
            icon_path=None,
            deleted_at=deleted_at,
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_name_management_tab_create_update_delete_restore_hard_delete() -> None:
    _app()
    core = StubCoreService()
    query = StubQueryService()
    tab = NameManagementTab(core_service=core, query_service=query)

    tab.operator_input.setText("op-1")
    tab.raw_name_input.setText("Created")
    tab._create_name()

    tab.names_table.selectRow(0)
    tab.raw_name_input.setText("Alice Updated")
    tab._update_name()
    tab._delete_name()

    tab.names_table.selectRow(1)
    tab._restore_name()
    tab._hard_delete_name()

    assert any(item.startswith("create:Created:op-1") for item in core.called)
    assert any(item.startswith("update:1:Alice Updated:op-1") for item in core.called)
    assert any(item.startswith("delete:1:op-1") for item in core.called)
    assert any(item.startswith("restore:2:op-1") for item in core.called)
    assert any(item.startswith("hard_delete:2:op-1") for item in core.called)


def test_name_management_tab_requires_operator_id() -> None:
    _app()
    tab = NameManagementTab(core_service=StubCoreService(), query_service=StubQueryService())
    tab.operator_input.setText("")
    tab._create_name()

    assert "operator_id" in tab.message_label.text()

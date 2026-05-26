"""UI tests for NameManagementTab."""

from __future__ import annotations

import os

import pytest

from app.application.read_models import NameDetail, NameSearchRow

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui import name_management_tab as name_tab_module  # noqa: E402
from app.ui.name_management_tab import NameManagementTab  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402


class StubCoreService:
    def __init__(self) -> None:
        self.called: list[str] = []

    def create_name(self, payload, operator_id: str, role: str = "admin") -> int:  # type: ignore[no-untyped-def]
        self.called.append(f"create:{payload.raw_name}:{operator_id}:{role}")
        return 1

    def update_name(self, name_id: int, payload, operator_id: str, role: str = "admin") -> None:  # type: ignore[no-untyped-def]
        self.called.append(f"update:{name_id}:{payload.raw_name}:{operator_id}:{role}")

    def delete_name(self, name_id: int, operator_id: str, role: str = "admin") -> None:
        self.called.append(f"delete:{name_id}:{operator_id}:{role}")

    def restore_name(self, name_id: int, operator_id: str, role: str = "admin") -> None:
        self.called.append(f"restore:{name_id}:{operator_id}:{role}")

    def hard_delete_name(
        self, name_id: int, operator_id: str, role: str = "admin"
    ) -> None:
        self.called.append(f"hard_delete:{name_id}:{operator_id}:{role}")


class StubQueryService:
    def __init__(self) -> None:
        self.last_query: str | None = None
        self.rows = [
            NameSearchRow(
                id=1,
                raw_name="Alice",
                normalized_name="alice",
                note=None,
                deleted_at=None,
                linked_count=3,
                title_ids=(),
                title_related_count=1,
                subtitle_related_count=2,
            ),
            NameSearchRow(
                id=2,
                raw_name="Bob",
                normalized_name="bob",
                note="memo",
                deleted_at="2026-01-01T00:00:00Z",
                linked_count=0,
                title_ids=(),
                title_related_count=0,
                subtitle_related_count=0,
            ),
        ]

    def search_names(self, *args: object, **kwargs: object) -> list[NameSearchRow]:
        _ = args
        query = kwargs.get("query")
        self.last_query = str(query) if query is not None else None
        return self.rows

    def get_name_detail(self, name_id: int, role: str = "admin") -> NameDetail:
        _ = role
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


def test_name_management_tab_has_workflow_tabs() -> None:
    _app()
    tab = NameManagementTab(core_service=StubCoreService(), query_service=StubQueryService())

    assert tab.property("workflow_tabs_layout") is True
    assert tab.workflow_tabs.count() == 5
    assert [tab.workflow_tabs.tabText(index) for index in range(5)] == [
        "一覧",
        "新規追加",
        "編集",
        "削除",
        "ガイド",
    ]
    assert tab.list_hint_label.property("accent") == "list"
    assert tab.add_hint_label.property("accent") == "add"
    assert tab.edit_hint_label.property("accent") == "edit"
    assert tab.delete_hint_label.property("accent") == "delete"


def test_name_management_tab_create_update_delete(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _app()
    monkeypatch.setattr(
        name_tab_module, "confirm_destructive_action", lambda *args, **kwargs: True
    )
    core = StubCoreService()
    query = StubQueryService()
    tab = NameManagementTab(core_service=core, query_service=query)

    tab.operator_input.setText("op-1")
    tab.workflow_tabs.setCurrentWidget(tab.add_tab)
    tab.add_raw_name_input.setText("Created")
    tab._create_name()

    tab.workflow_tabs.setCurrentWidget(tab.edit_tab)
    tab.names_table.selectRow(0)
    tab.raw_name_input.setText("Alice Updated")
    tab._update_name()

    tab.workflow_tabs.setCurrentWidget(tab.delete_tab)
    tab.delete_name_selector.setCurrentIndex(1)
    tab._delete_name()

    assert any(item.startswith("create:Created:op-1:admin") for item in core.called)
    assert any(
        item.startswith("update:1:Alice Updated:op-1:admin")
        for item in core.called
    )
    assert any(item.startswith("delete:1:op-1:admin") for item in core.called)

    assert tab.names_table.columnCount() == 9
    assert tab.names_table.item(0, 1).text() == "未採番"
    assert tab.names_table.item(0, 2).text() == "Alice"
    assert tab.names_table.item(0, 5).text() == "1"
    assert tab.names_table.item(0, 6).text() == "2"
    assert tab.names_table.item(0, 7).text() == "3"

    tab.filter_input.setText("ali")
    tab._refresh_list()
    assert query.last_query == "ali"


def test_name_add_tab_does_not_use_previous_selection() -> None:
    _app()
    tab = NameManagementTab(core_service=StubCoreService(), query_service=StubQueryService())

    tab.names_table.selectRow(0)
    tab.workflow_tabs.setCurrentWidget(tab.add_tab)

    assert tab.add_raw_name_input.text() == ""
    assert tab.add_note_input.text() == ""
    assert tab.raw_name_input.text() == "Alice"


def test_name_management_tab_requires_operator_id() -> None:
    _app()
    tab = NameManagementTab(core_service=StubCoreService(), query_service=StubQueryService())
    tab.operator_input.setText("")
    tab._create_name()

    assert "操作者ID" in tab.message_label.text()


def test_name_management_cancel_does_not_call_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _app()
    monkeypatch.setattr(
        name_tab_module, "confirm_destructive_action", lambda *args, **kwargs: False
    )
    core = StubCoreService()
    tab = NameManagementTab(core_service=core, query_service=StubQueryService())
    tab.operator_input.setText("op-1")

    tab.names_table.selectRow(0)
    tab._delete_name()

    assert not any(item.startswith("delete:") for item in core.called)


def test_name_management_role_guards() -> None:
    _app()
    tab_viewer = NameManagementTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(),
        role_context=RoleContext(role="viewer"),
    )
    assert not tab_viewer.create_button.isEnabled()
    assert not tab_viewer.update_button.isEnabled()
    assert not tab_viewer.delete_button.isEnabled()
    assert "このロールでは実行できません" in tab_viewer.delete_button.toolTip()

    tab_editor = NameManagementTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(),
        role_context=RoleContext(role="editor"),
    )
    assert tab_editor.create_button.isEnabled()
    tab_editor.names_table.selectRow(0)
    assert tab_editor.update_button.isEnabled()
    assert not tab_editor.delete_button.isEnabled()

    tab_admin = NameManagementTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(),
        role_context=RoleContext(role="admin"),
    )
    tab_admin.names_table.selectRow(0)
    assert tab_admin.delete_button.isEnabled()
    assert tab_admin.restore_button.isHidden()
    assert tab_admin.hard_delete_button.isHidden()
    assert "自動入力" in tab_admin.operator_input.toolTip()


def test_name_management_propagates_editor_role_to_service() -> None:
    _app()
    core = StubCoreService()
    tab = NameManagementTab(
        core_service=core,
        query_service=StubQueryService(),
        role_context=RoleContext(role="editor"),
    )
    tab.operator_input.setText("op-1")
    tab.workflow_tabs.setCurrentWidget(tab.add_tab)
    tab.add_raw_name_input.setText("EditorCreate")
    tab._create_name()

    assert "create:EditorCreate:op-1:editor" in core.called

"""UI regression tests for delete-flow clarity and user-management polish."""

from __future__ import annotations

import os

import pytest

from app.application.user_services import UserRecord

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui import trash_tab as trash_tab_module  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402
from app.ui.trash_tab import TrashTab  # noqa: E402
from app.ui.user_management_tab import UserManagementTab  # noqa: E402
from tests.test_trash_tab_ui import StubCoreService, StubQueryService  # noqa: E402


class StubUserService:
    def __init__(self) -> None:
        self.users = [
            UserRecord(
                id=1,
                public_id="user-public-admin",
                operator_id="admin",
                display_name="Admin User",
                role="admin",
                auth_provider="local",
                windows_account_name=None,
                windows_sid=None,
                disabled_at=None,
                failed_login_count=0,
                locked_until=None,
                last_login_at="2026-01-01T00:00:00Z",
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            ),
            UserRecord(
                id=2,
                public_id="user-public-viewer",
                operator_id="viewer",
                display_name="Viewer User",
                role="viewer",
                auth_provider="windows",
                windows_account_name="DOMAIN\\viewer",
                windows_sid="S-1-5-21-1",
                disabled_at="2026-02-01T00:00:00Z",
                failed_login_count=2,
                locked_until=None,
                last_login_at=None,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-02-01T00:00:00Z",
            ),
        ]

    def list_users(self, *, include_disabled: bool = False) -> list[UserRecord]:
        _ = include_disabled
        return self.users

    def create_user(self, *args: object, **kwargs: object) -> int:
        _ = (args, kwargs)
        return 3

    def change_user_role(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)

    def disable_user(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)

    def enable_user(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_trash_tab_shows_selected_target_summary_and_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _app()
    confirmation_messages: list[str] = []

    def confirm(_parent: object, _title: str, message: str) -> bool:
        confirmation_messages.append(message)
        return True

    monkeypatch.setattr(trash_tab_module, "confirm_destructive_action", confirm)
    core = StubCoreService()
    tab = TrashTab(core_service=core, query_service=StubQueryService())
    tab.operator_input.setText("op-1")
    tab.entity_selector.setCurrentText("Name")

    assert tab.restore_button.text() == "選択データを復元"
    assert tab.hard_delete_button.text() == "選択データを完全削除"
    assert tab.selected_summary_label.property("selected_target_summary") is True
    assert "選択中: 名前" in tab.selected_summary_label.text()
    assert "表示名=Alice" in tab.selected_summary_label.text()
    assert "内部ID=1" in tab.selected_summary_label.text()

    tab._hard_delete_selected()

    assert "表示名=Alice" in confirmation_messages[-1]
    assert "操作者ID: op-1" in confirmation_messages[-1]
    assert "hard_delete_name:1:op-1:admin" in core.calls


def test_user_management_tab_shows_counts_and_selected_user_summary() -> None:
    _app()
    tab = UserManagementTab(
        user_service=StubUserService(),  # type: ignore[arg-type]
        role_context=RoleContext.admin(),
    )

    assert tab.user_count_summary_label.property("user_count_summary") is True
    assert "全2件" in tab.user_count_summary_label.text()
    assert "有効1件" in tab.user_count_summary_label.text()
    assert "無効1件" in tab.user_count_summary_label.text()
    assert "ローカル1" in tab.user_count_summary_label.text()
    assert "Windows1" in tab.user_count_summary_label.text()
    assert tab.table.horizontalHeaderItem(8).text() == "公開ID"
    assert tab.table.item(0, 2).text() == "管理者"
    assert tab.table.item(1, 2).text() == "閲覧者"
    assert tab.table.item(1, 3).text() == "Windows"

    tab.table.selectRow(1)
    tab._copy_selected_operator()

    assert tab.target_operator_input.text() == "viewer"
    assert tab.selected_user_summary_label.property("selected_user_summary") is True
    assert "操作者ID=viewer" in tab.selected_user_summary_label.text()
    assert "表示名=Viewer User" in tab.selected_user_summary_label.text()
    assert "権限=閲覧者" in tab.selected_user_summary_label.text()
    assert "状態=無効" in tab.selected_user_summary_label.text()


def test_user_management_tab_non_admin_summary_is_read_only() -> None:
    _app()
    tab = UserManagementTab(
        user_service=StubUserService(),  # type: ignore[arg-type]
        role_context=RoleContext(role="viewer"),
    )

    assert "adminのみ表示できます" in tab.user_count_summary_label.text()
    assert "権限不足" in tab.selected_user_summary_label.text()
    assert not tab.change_role_button.isEnabled()
    assert not tab.disable_button.isEnabled()

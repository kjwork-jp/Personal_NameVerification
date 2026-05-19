"""Release UAT coverage for authentication, RBAC, and key UI tabs."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pytest

from app.application.read_models import (
    ChangeLogRow,
    NameSearchRow,
    RelatedRow,
    SubtitleDetail,
    TitleDetail,
    UserAuditLogRow,
)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication
QLabel = qt_widgets.QLabel

from app.application.user_services import CreateUserInput, UserService  # noqa: E402
from app.application.windows_identity import WindowsIdentity  # noqa: E402
from app.domain.errors import AuthorizationError  # noqa: E402
from app.infrastructure.db import apply_schema  # noqa: E402
from app.ui.audit_logs_tab import AuditLogsTab  # noqa: E402
from app.ui.main_window import MainWindow  # noqa: E402
from app.ui.operations_tab import OperationsTab  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402
from app.ui.title_subtitle_unified_tab import TitleSubtitleUnifiedTab  # noqa: E402
from tests.test_main_window_smoke import (  # noqa: E402
    EmptyBackupRestoreService,
    EmptyCoreService,
    EmptyExportBackupService,
    EmptyImportService,
    _patch_operations_dependencies,
)


class UatQueryService:
    def search_names(self, *args: object, **kwargs: object) -> list[NameSearchRow]:
        _ = (args, kwargs)
        return [
            NameSearchRow(
                id=1,
                raw_name="Alice",
                normalized_name="alice",
                note=None,
                deleted_at=None,
                linked_count=1,
                title_ids=(10,),
                public_id="name-public-id-001",
            )
        ]

    def get_name_detail(self, name_id: int) -> object:
        raise RuntimeError(f"not used: {name_id}")

    def list_titles(
        self, role: str = "admin", *, include_deleted: bool = False
    ) -> list[TitleDetail]:
        _ = (role, include_deleted)
        return [
            TitleDetail(
                id=10,
                title_name="Title1",
                note="title-note",
                icon_path=None,
                deleted_at=None,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
                public_id="title-public-id-001",
            )
        ]

    def list_subtitles(
        self, title_id: int, role: str = "admin", *, include_deleted: bool = False
    ) -> list[SubtitleDetail]:
        _ = (title_id, role, include_deleted)
        return [
            SubtitleDetail(
                id=100,
                title_id=10,
                subtitle_code="S1",
                subtitle_name="Sub1",
                sort_order=1,
                note="subtitle-note",
                icon_path=None,
                deleted_at=None,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
                public_id="subtitle-public-id-001",
            )
        ]

    def list_names_for_title(
        self, title_id: int, role: str = "admin", *, include_deleted: bool = False
    ) -> list[object]:
        _ = (title_id, role, include_deleted)
        return []

    def list_related_rows(
        self, name_id: int, role: str = "admin", *, include_deleted: bool = False
    ) -> list[RelatedRow]:
        _ = (name_id, role, include_deleted)
        return [
            RelatedRow(
                link_id=500,
                name_id=1,
                subtitle_id=100,
                title_id=10,
                relation_type="primary",
                subtitle_code="S1",
                subtitle_name="Sub1",
                title_name="Title1",
                link_deleted_at=None,
                link_public_id="link-public-id-001",
                name_public_id="name-public-id-001",
                subtitle_public_id="subtitle-public-id-001",
                title_public_id="title-public-id-001",
            )
        ]

    def list_change_logs(self, *args: object, **kwargs: object) -> list[ChangeLogRow]:
        _ = (args, kwargs)
        return [
            ChangeLogRow(
                id=1,
                entity_type="names",
                entity_id=1,
                action="update",
                operator_id="admin",
                before_json='{"raw_name":"Alice"}',
                after_json='{"raw_name":"Alice Updated"}',
                created_at="2026-01-01T00:00:00Z",
                public_id="change-public-id-001",
            )
        ]

    def list_deleted_names(self) -> list[object]:
        return []

    def list_deleted_titles(self) -> list[object]:
        return []

    def list_deleted_subtitles(self) -> list[object]:
        return []

    def list_deleted_links(self) -> list[object]:
        return []


class StubUserAuditService:
    def list_user_audit_logs(self, *args: object, **kwargs: object) -> list[UserAuditLogRow]:
        _ = (args, kwargs)
        return [
            UserAuditLogRow(
                id=1,
                actor_operator_id="admin",
                target_operator_id="editor",
                action="login_success",
                before_json=None,
                after_json='{"auth_provider":"local"}',
                created_at="2026-01-01T00:00:00Z",
            )
        ]


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    apply_schema(connection)
    return connection


def _window_for_role(
    role: str,
    monkeypatch: pytest.MonkeyPatch,
    *,
    user_audit_service: object | None = None,
) -> MainWindow:
    _app()
    _patch_operations_dependencies(monkeypatch)
    return MainWindow(
        query_service=UatQueryService(),
        core_service=EmptyCoreService(),
        role_context=RoleContext(role=role, operator_id=f"{role}-operator"),
        export_backup_service=EmptyExportBackupService(),
        backup_restore_service=EmptyBackupRestoreService(),
        import_service=EmptyImportService(),
        user_audit_service=user_audit_service,
        database_path=Path("release-uat-test.db"),
    )


def _operations(window: MainWindow) -> OperationsTab:
    tab = window._tabs_by_name["データ入出力"]
    assert isinstance(tab, OperationsTab)
    return tab


def _operation_subtab_visibility(window: MainWindow) -> dict[str, bool]:
    sub_tabs = _operations(window).operations_subtabs
    return {
        sub_tabs.tabText(index): sub_tabs.tabBar().isTabVisible(index)
        for index in range(sub_tabs.count())
    }


def _link_subtab_visibility(window: MainWindow) -> dict[str, bool]:
    link_tab = window._tabs_by_name["関連付け"]
    sub_tabs = link_tab.tabs
    return {
        sub_tabs.tabText(index): sub_tabs.tabBar().isTabVisible(index)
        for index in range(sub_tabs.count())
    }


def test_uat_auth_local_and_windows_authentication_flows() -> None:
    connection = _connection()
    service = UserService(connection)
    service.create_user(
        CreateUserInput(operator_id="admin", password="secret", role="admin"),
        actor_operator_id="bootstrap",
        actor_role="admin",
    )

    local_user = service.authenticate_user("admin", "secret")
    assert local_user.auth_provider == "local"
    assert local_user.role == "admin"

    identity = WindowsIdentity(
        account_name="DOMAIN\\naoki",
        display_name="naoki",
        sid="S-1-5-21-1000",
    )
    windows_user = service.authenticate_windows_user(identity)
    assert windows_user.auth_provider == "windows"
    assert windows_user.role == "viewer"

    service.change_user_role(
        windows_user.operator_id,
        "editor",
        actor_operator_id="admin",
        actor_role="admin",
    )
    reused_windows_user = service.authenticate_windows_user(identity)
    assert reused_windows_user.operator_id == windows_user.operator_id
    assert reused_windows_user.role == "editor"

    with pytest.raises(AuthorizationError):
        service.authenticate_user(windows_user.operator_id, "any-password")


def test_uat_rbac_and_data_io_visibility_by_role(monkeypatch: pytest.MonkeyPatch) -> None:
    viewer = _window_for_role("viewer", monkeypatch)
    editor = _window_for_role("editor", monkeypatch)
    admin = _window_for_role("admin", monkeypatch)

    assert _operation_subtab_visibility(viewer) == {
        "ガイド": True,
        "Export": False,
        "Backup": False,
        "Restore": False,
        "Import": False,
        "Operations Log": True,
    }
    assert _operation_subtab_visibility(editor) == {
        "ガイド": True,
        "Export": True,
        "Backup": True,
        "Restore": False,
        "Import": False,
        "Operations Log": True,
    }
    assert _operation_subtab_visibility(admin) == {
        "ガイド": True,
        "Export": True,
        "Backup": True,
        "Restore": True,
        "Import": True,
        "Operations Log": True,
    }

    viewer_name = viewer._tabs_by_name["名前を管理"]
    editor_name = editor._tabs_by_name["名前を管理"]
    admin_name = admin._tabs_by_name["名前を管理"]
    assert viewer_name.raw_name_input.isHidden()
    assert viewer_name.create_button.isHidden()
    assert not editor_name.create_button.isHidden()
    assert editor_name.delete_button.isHidden()
    assert not admin_name.delete_button.isHidden()


def test_uat_audit_logs_unified_tabs_and_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    window = _window_for_role(
        "admin",
        monkeypatch,
        user_audit_service=StubUserAuditService(),
    )
    audit_tab = window._tabs_by_name["監査ログ"]
    assert isinstance(audit_tab, AuditLogsTab)

    assert [audit_tab.tabs.tabText(index) for index in range(audit_tab.tabs.count())] == [
        "データ変更ログ",
        "ユーザー/認証ログ",
        "ガイド",
    ]
    assert audit_tab.data_change_tab.logs_table.rowCount() == 1
    assert audit_tab.user_audit_tab is not None
    assert audit_tab.user_audit_tab.logs_table.rowCount() == 1

    guide_text = "\n".join(label.text() for label in audit_tab.findChildren(QLabel))
    assert "データ変更ログ" in guide_text
    assert "ユーザー/認証ログ" in guide_text
    assert "Operations Log" in guide_text


def test_uat_title_and_link_visibility_by_role(monkeypatch: pytest.MonkeyPatch) -> None:
    viewer = _window_for_role("viewer", monkeypatch)
    editor = _window_for_role("editor", monkeypatch)
    admin = _window_for_role("admin", monkeypatch)

    viewer_title = viewer._tabs_by_name["タイトル/サブタイトル管理"]
    assert isinstance(viewer_title, TitleSubtitleUnifiedTab)
    viewer_title_editor = viewer_title.title_tab.editor
    assert viewer_title_editor.title_name_input.isHidden()
    assert viewer_title_editor.title_create_button.isHidden()
    assert viewer_title_editor.title_delete_button.isHidden()

    editor_title = editor._tabs_by_name["タイトル/サブタイトル管理"]
    assert isinstance(editor_title, TitleSubtitleUnifiedTab)
    editor_title_editor = editor_title.title_tab.editor
    assert not editor_title_editor.title_create_button.isHidden()
    assert editor_title_editor.title_delete_button.isHidden()

    admin_title = admin._tabs_by_name["タイトル/サブタイトル管理"]
    assert isinstance(admin_title, TitleSubtitleUnifiedTab)
    assert not admin_title.title_tab.editor.title_delete_button.isHidden()

    assert _link_subtab_visibility(viewer) == {"登録": False, "解除": False}
    assert _link_subtab_visibility(editor) == {"登録": True, "解除": False}
    assert _link_subtab_visibility(admin) == {"登録": True, "解除": True}

    admin_link = admin._tabs_by_name["関連付け"]
    assert admin_link.register_name_combo.itemText(0) == "名前: Alice（公開ID: name-public-id-001）"
    assert "..." not in admin_link.register_name_combo.itemText(0)
    assert "…" not in admin_link.register_name_combo.itemText(0)

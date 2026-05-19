"""RBAC UI guard regression tests for main tabs."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication
QLabel = qt_widgets.QLabel
QPushButton = qt_widgets.QPushButton

from app.ui.main_window import MainWindow  # noqa: E402
from app.ui.operations_tab import OperationsTab  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402
from tests.test_main_window_smoke import (  # noqa: E402
    EmptyBackupRestoreService,
    EmptyCoreService,
    EmptyExportBackupService,
    EmptyImportService,
    EmptyQueryService,
    _patch_operations_dependencies,
)


class EmptyUserService:
    def list_users(self, *, include_disabled: bool = False) -> list[object]:
        _ = include_disabled
        return []


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _window_for_role(role: str, monkeypatch: pytest.MonkeyPatch) -> MainWindow:
    _app()
    _patch_operations_dependencies(monkeypatch)
    return MainWindow(
        query_service=EmptyQueryService(),
        core_service=EmptyCoreService(),
        role_context=RoleContext(role=role),
        export_backup_service=EmptyExportBackupService(),
        backup_restore_service=EmptyBackupRestoreService(),
        import_service=EmptyImportService(),
        database_path=Path("rbac-ui-test.db"),
    )


def _window_with_user_service(role: str, monkeypatch: pytest.MonkeyPatch) -> MainWindow:
    _app()
    _patch_operations_dependencies(monkeypatch)
    return MainWindow(
        query_service=EmptyQueryService(),
        core_service=EmptyCoreService(),
        role_context=RoleContext(role=role),
        export_backup_service=EmptyExportBackupService(),
        backup_restore_service=EmptyBackupRestoreService(),
        import_service=EmptyImportService(),
        user_service=EmptyUserService(),  # type: ignore[arg-type]
        database_path=Path("rbac-ui-test.db"),
    )


def _button(window: MainWindow, tab_title: str, attr_name: str) -> QPushButton:
    tab = window._tabs_by_name[tab_title]
    button = getattr(tab, attr_name)
    assert isinstance(button, QPushButton)
    return button


def _operations(window: MainWindow) -> OperationsTab:
    tab = window._tabs_by_name["データ入出力"]
    assert isinstance(tab, OperationsTab)
    return tab


def _tab_titles(window: MainWindow) -> list[str]:
    return [window.tabs.tabText(index) for index in range(window.tabs.count())]


def _operations_subtab_enabled_map(window: MainWindow) -> dict[str, bool]:
    sub_tabs = _operations(window).operations_subtabs
    return {
        sub_tabs.tabText(index): sub_tabs.isTabEnabled(index)
        for index in range(sub_tabs.count())
    }


def _operations_subtab_visible_map(window: MainWindow) -> dict[str, bool]:
    sub_tabs = _operations(window).operations_subtabs
    return {
        sub_tabs.tabText(index): sub_tabs.tabBar().isTabVisible(index)
        for index in range(sub_tabs.count())
    }


def _operations_guide_text(window: MainWindow) -> str:
    guide_label = _operations(window).findChild(QLabel, "operationsRoleGuideLabel")
    assert guide_label is not None
    return guide_label.text()


def test_viewer_rbac_disables_write_and_destructive_controls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = _window_for_role("viewer", monkeypatch)
    operations = _operations(window)

    assert not _button(window, "名前を管理", "create_button").isEnabled()
    assert not _button(window, "名前を管理", "update_button").isEnabled()
    assert not _button(window, "名前を管理", "delete_button").isEnabled()
    assert not _button(window, "関連付け", "link_button").isEnabled()
    assert not _button(window, "関連付け", "unlink_button").isEnabled()
    assert not _button(window, "削除データ", "restore_button").isEnabled()
    assert not _button(window, "削除データ", "hard_delete_button").isEnabled()

    assert not operations.export_csv_button.isEnabled()
    assert not operations.create_backup_button.isEnabled()
    assert not operations.restore_button.isEnabled()
    assert not operations.import_csv_button.isEnabled()
    assert not operations.export_logs_button.isEnabled()
    assert not operations.export_logs_button.isVisible()


def test_editor_rbac_allows_normal_write_and_export_backup_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = _window_for_role("editor", monkeypatch)
    operations = _operations(window)

    assert _button(window, "名前を管理", "create_button").isEnabled()
    assert _button(window, "名前を管理", "update_button").isEnabled()
    assert not _button(window, "名前を管理", "delete_button").isEnabled()
    assert _button(window, "関連付け", "link_button").isEnabled()
    assert not _button(window, "関連付け", "unlink_button").isEnabled()
    assert not _button(window, "削除データ", "restore_button").isEnabled()
    assert not _button(window, "削除データ", "hard_delete_button").isEnabled()

    assert operations.export_csv_button.isEnabled()
    assert operations.export_json_button.isEnabled()
    assert operations.export_sql_dump_button.isEnabled()
    assert operations.create_backup_button.isEnabled()
    assert not operations.restore_button.isEnabled()
    assert not operations.import_csv_button.isEnabled()
    assert not operations.import_json_button.isEnabled()
    assert operations.export_logs_button.isEnabled()


def test_admin_rbac_allows_destructive_and_management_controls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = _window_for_role("admin", monkeypatch)
    operations = _operations(window)

    assert _button(window, "名前を管理", "create_button").isEnabled()
    assert _button(window, "名前を管理", "update_button").isEnabled()
    assert _button(window, "名前を管理", "delete_button").isEnabled()
    assert _button(window, "関連付け", "link_button").isEnabled()
    assert _button(window, "関連付け", "unlink_button").isEnabled()
    assert _button(window, "削除データ", "restore_button").isEnabled()
    assert _button(window, "削除データ", "hard_delete_button").isEnabled()

    assert operations.export_csv_button.isEnabled()
    assert operations.create_backup_button.isEnabled()
    assert operations.restore_button.isEnabled()
    assert operations.import_csv_button.isEnabled()
    assert operations.import_json_button.isEnabled()
    assert operations.export_logs_button.isEnabled()


def test_operations_cancel_button_is_visible_only_while_busy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    operations = _operations(_window_for_role("admin", monkeypatch))

    assert operations.cancel_operation_button.isHidden()

    operations._is_busy = True
    operations._apply_busy_state()
    assert not operations.cancel_operation_button.isHidden()
    assert operations.cancel_operation_button.isEnabled()

    operations._is_busy = False
    operations._apply_busy_state()
    assert operations.cancel_operation_button.isHidden()
    assert not operations.cancel_operation_button.isEnabled()


def test_user_management_tab_is_admin_only_when_user_service_is_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    viewer_window = _window_with_user_service("viewer", monkeypatch)
    editor_window = _window_with_user_service("editor", monkeypatch)
    admin_window = _window_with_user_service("admin", monkeypatch)

    assert "ユーザー管理" not in _tab_titles(viewer_window)
    assert "ユーザー管理" not in viewer_window._tabs_by_name
    assert "ユーザー管理" not in _tab_titles(editor_window)
    assert "ユーザー管理" not in editor_window._tabs_by_name
    assert "ユーザー管理" in _tab_titles(admin_window)
    assert "ユーザー管理" in admin_window._tabs_by_name


def test_operations_subtabs_are_role_aware(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _operations_subtab_enabled_map(_window_for_role("viewer", monkeypatch)) == {
        "ガイド": True,
        "Export": False,
        "Backup": False,
        "Restore": False,
        "Import": False,
        "Operations Log": True,
    }
    assert _operations_subtab_enabled_map(_window_for_role("editor", monkeypatch)) == {
        "ガイド": True,
        "Export": True,
        "Backup": True,
        "Restore": False,
        "Import": False,
        "Operations Log": True,
    }
    assert _operations_subtab_enabled_map(_window_for_role("admin", monkeypatch)) == {
        "ガイド": True,
        "Export": True,
        "Backup": True,
        "Restore": True,
        "Import": True,
        "Operations Log": True,
    }


def test_unavailable_operations_subtabs_are_hidden(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _operations_subtab_visible_map(_window_for_role("viewer", monkeypatch)) == {
        "ガイド": True,
        "Export": False,
        "Backup": False,
        "Restore": False,
        "Import": False,
        "Operations Log": True,
    }
    assert _operations_subtab_visible_map(_window_for_role("editor", monkeypatch)) == {
        "ガイド": True,
        "Export": True,
        "Backup": True,
        "Restore": False,
        "Import": False,
        "Operations Log": True,
    }
    assert _operations_subtab_visible_map(_window_for_role("admin", monkeypatch)) == {
        "ガイド": True,
        "Export": True,
        "Backup": True,
        "Restore": True,
        "Import": True,
        "Operations Log": True,
    }


def test_operations_guide_text_matches_visible_role_scope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    viewer_guide = _operations_guide_text(_window_for_role("viewer", monkeypatch))
    editor_guide = _operations_guide_text(_window_for_role("editor", monkeypatch))
    admin_guide = _operations_guide_text(_window_for_role("admin", monkeypatch))

    assert "操作ガイド（viewer）" in viewer_guide
    assert "実行ログの参照のみ" in viewer_guide
    assert "Export / Backup / Restore / Import は表示しません" in viewer_guide

    assert "操作ガイド（editor）" in editor_guide
    assert "通常の出力とバックアップのみ" in editor_guide
    assert "Restore / Import は破壊的操作のため表示しません" in editor_guide

    assert "操作ガイド（admin）" in admin_guide
    assert "データ入出力の全操作" in admin_guide
    assert "Restore" in admin_guide
    assert "Import" in admin_guide

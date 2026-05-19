"""PySide6 formal entrypoint for NameVerification v3."""

from __future__ import annotations

import sys
from functools import partial
from typing import Protocol


class _ApplicationLike(Protocol):
    def quit(self) -> None: ...


class _ClosableWidget(Protocol):
    def close(self) -> bool: ...

    def deleteLater(self) -> None: ...


def _hide_combo_popups(current_window: _ClosableWidget) -> None:
    """Hide combo/completer popups that can survive account switching."""

    from PySide6.QtWidgets import QApplication, QComboBox, QWidget

    candidate_windows = list(QApplication.topLevelWidgets())
    if isinstance(current_window, QWidget) and current_window not in candidate_windows:
        candidate_windows.append(current_window)

    seen_combo_ids: set[int] = set()
    for widget in candidate_windows:
        for combo in widget.findChildren(QComboBox):
            combo_id = id(combo)
            if combo_id in seen_combo_ids:
                continue
            seen_combo_ids.add(combo_id)

            combo.hidePopup()
            completer = combo.completer()
            if completer is None:
                continue

            popup = completer.popup()
            if popup is not None:
                popup.hide()
                popup.close()


def _close_account_switch_widgets(
    app: _ApplicationLike,
    current_window: _ClosableWidget,
) -> None:
    """Close stray popup/top-level widgets before returning to login.

    QComboBox/QCompleter popups and hidden role-guarded widgets can remain as
    native top-level windows if account switching occurs while they are active.
    During account switching, last-window auto-quit is disabled temporarily so
    closing the current MainWindow does not terminate the outer login loop before
    the explicit quit request is handled.
    """

    from PySide6.QtWidgets import QApplication

    QApplication.setQuitOnLastWindowClosed(False)

    _hide_combo_popups(current_window)
    QApplication.processEvents()

    active_popup = QApplication.activePopupWidget()
    if active_popup is not None and active_popup is not current_window:
        active_popup.hide()
        active_popup.close()

    for widget in list(QApplication.topLevelWidgets()):
        if widget is current_window:
            continue
        widget.hide()
        widget.close()
        widget.deleteLater()

    QApplication.processEvents()
    _hide_combo_popups(current_window)

    current_window.close()
    QApplication.processEvents()
    app.quit()


def main() -> int:
    """Launch the PySide6 application shell."""
    from PySide6.QtWidgets import QApplication, QDialog

    from app.application.auto_log_export import AutoExportingCoreService
    from app.application.backup_restore_services import BackupRestoreService
    from app.application.enhanced_query_services import EnhancedQueryService
    from app.application.export_backup_services import ExportBackupService
    from app.application.import_services import ImportService
    from app.application.runtime_paths import (
        ensure_runtime_parent_dirs,
        resolve_change_log_jsonl_path,
        resolve_database_path,
        resolve_operations_log_jsonl_path,
        resolve_package_root,
    )
    from app.application.user_audit_services import UserAuditLogService
    from app.application.user_services import UserService
    from app.infrastructure.db import initialize_database
    from app.ui.initial_admin_setup_dialog import InitialAdminSetupDialog
    from app.ui.login_dialog import LoginDialog
    from app.ui.main_window import MainWindow
    from app.ui.operations_log import OperationsJsonlLogger
    from app.ui.role_context import RoleContext
    from app.ui.ui_style import ensure_positive_application_font

    package_root = resolve_package_root()
    database_path = resolve_database_path(package_root=package_root)
    change_log_jsonl_path = resolve_change_log_jsonl_path(package_root=package_root)
    operations_log_jsonl_path = resolve_operations_log_jsonl_path(package_root=package_root)
    ensure_runtime_parent_dirs(database_path, change_log_jsonl_path, operations_log_jsonl_path)

    connection = initialize_database(database_path)
    query_service = EnhancedQueryService(connection)
    core_service = AutoExportingCoreService(connection, log_path=change_log_jsonl_path)
    user_service = UserService(connection)
    user_audit_service = UserAuditLogService(connection)

    app = QApplication(sys.argv)
    ensure_positive_application_font(app)
    operation_logger = OperationsJsonlLogger(log_path=operations_log_jsonl_path)

    def _append_operation_log(
        *,
        action: str,
        role_context: RoleContext,
        message: str,
    ) -> None:
        try:
            operation_logger.append(
                action=action,
                role=role_context.role,
                status="success",
                message=message,
                path=str(database_path),
                path2=str(change_log_jsonl_path),
            )
        except Exception:
            pass

    def _ensure_initial_admin() -> bool:
        if user_service.list_users(include_disabled=False):
            return True
        setup = InitialAdminSetupDialog(user_service)
        return setup.exec() == QDialog.DialogCode.Accepted

    if not _ensure_initial_admin():
        connection.close()
        return 0

    exit_code = 0
    while True:
        # LoginDialog is a nested modal loop. Keep last-window auto-quit disabled
        # here so stale popup cleanup from account switching cannot close an empty
        # login shell before its child widgets finish painting.
        QApplication.setQuitOnLastWindowClosed(False)
        login = LoginDialog(user_service)
        if login.exec() != QDialog.DialogCode.Accepted:
            break

        role_context = login.role_context()
        _append_operation_log(
            action="app_startup",
            role_context=role_context,
            message="Application startup",
        )

        account_switch_requested = False
        window = MainWindow(
            query_service=query_service,
            core_service=core_service,
            role_context=role_context,
            export_backup_service=ExportBackupService(connection, database_path=database_path),
            backup_restore_service=BackupRestoreService(),
            import_service=ImportService(connection, database_path=database_path),
            user_service=user_service,
            user_audit_service=user_audit_service,
            package_root=package_root,
            database_path=database_path,
            change_log_jsonl_path=change_log_jsonl_path,
            operations_log_jsonl_path=operations_log_jsonl_path,
            operation_logger=operation_logger,
            connection=connection,
        )

        def _request_account_switch(
            current_role_context: RoleContext,
            current_window: MainWindow,
        ) -> None:
            nonlocal account_switch_requested
            account_switch_requested = True
            _append_operation_log(
                action="account_switch",
                role_context=current_role_context,
                message=f"Account switch requested by {current_role_context.operator_id}",
            )
            _close_account_switch_widgets(app, current_window)

        window.account_switch_requested.connect(
            partial(_request_account_switch, role_context, window)
        )
        window.show()

        QApplication.setQuitOnLastWindowClosed(True)
        exit_code = int(app.exec())
        if account_switch_requested:
            QApplication.setQuitOnLastWindowClosed(False)
            window.deleteLater()
            QApplication.processEvents()
            continue
        break

    connection.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

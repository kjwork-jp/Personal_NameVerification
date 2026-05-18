"""PySide6 formal entrypoint for NameVerification v3."""

from __future__ import annotations

import sys


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

        def _request_account_switch() -> None:
            nonlocal account_switch_requested
            account_switch_requested = True
            _append_operation_log(
                action="account_switch",
                role_context=role_context,
                message=f"Account switch requested by {role_context.operator_id}",
            )
            window.close()

        window.account_switch_requested.connect(_request_account_switch)
        window.show()

        exit_code = int(app.exec())
        if account_switch_requested:
            continue
        break

    connection.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

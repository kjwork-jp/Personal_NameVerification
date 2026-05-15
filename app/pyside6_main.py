"""PySide6 formal entrypoint for NameVerification v3."""

from __future__ import annotations

import sys


def main() -> int:
    """Launch the minimal PySide6 application shell."""
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
    from app.application.user_services import UserService
    from app.infrastructure.db import initialize_database
    from app.ui.initial_admin_setup_dialog import InitialAdminSetupDialog
    from app.ui.login_dialog import LoginDialog
    from app.ui.main_window import MainWindow
    from app.ui.operations_log import OperationsJsonlLogger

    package_root = resolve_package_root()
    database_path = resolve_database_path(package_root=package_root)
    change_log_jsonl_path = resolve_change_log_jsonl_path(package_root=package_root)
    operations_log_jsonl_path = resolve_operations_log_jsonl_path(package_root=package_root)
    ensure_runtime_parent_dirs(database_path, change_log_jsonl_path, operations_log_jsonl_path)

    connection = initialize_database(database_path)
    query_service = EnhancedQueryService(connection)
    core_service = AutoExportingCoreService(connection, log_path=change_log_jsonl_path)
    user_service = UserService(connection)

    app = QApplication(sys.argv)
    operation_logger = OperationsJsonlLogger(log_path=operations_log_jsonl_path)
    if not user_service.list_users(include_disabled=False):
        setup = InitialAdminSetupDialog(user_service)
        if setup.exec() != QDialog.DialogCode.Accepted:
            connection.close()
            return 0

    login = LoginDialog(user_service)
    if login.exec() != QDialog.DialogCode.Accepted:
        connection.close()
        return 0
    role_context = login.role_context()
    try:
        operation_logger.append(
            action="app_startup",
            role=role_context.role,
            status="success",
            message="Application startup",
            path=str(database_path),
            path2=str(change_log_jsonl_path),
        )
    except Exception:
        pass

    window = MainWindow(
        query_service=query_service,
        core_service=core_service,
        role_context=role_context,
        export_backup_service=ExportBackupService(connection, database_path=database_path),
        backup_restore_service=BackupRestoreService(),
        import_service=ImportService(connection, database_path=database_path),
        package_root=package_root,
        database_path=database_path,
        change_log_jsonl_path=change_log_jsonl_path,
        operations_log_jsonl_path=operations_log_jsonl_path,
        operation_logger=operation_logger,
        connection=connection,
    )
    window.show()

    return int(app.exec())


if __name__ == "__main__":
    raise SystemExit(main())
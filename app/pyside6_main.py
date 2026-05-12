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
        resolve_package_root,
    )
    from app.infrastructure.db import initialize_database
    from app.ui.login_dialog import LoginDialog
    from app.ui.main_window import MainWindow

    package_root = resolve_package_root()
    database_path = resolve_database_path(package_root=package_root)
    change_log_jsonl_path = resolve_change_log_jsonl_path(package_root=package_root)
    ensure_runtime_parent_dirs(database_path, change_log_jsonl_path)

    connection = initialize_database(database_path)
    query_service = EnhancedQueryService(connection)
    core_service = AutoExportingCoreService(connection, log_path=change_log_jsonl_path)

    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec() != QDialog.DialogCode.Accepted:
        connection.close()
        return 0
    role_context = login.role_context()

    window = MainWindow(
        query_service=query_service,
        core_service=core_service,
        role_context=role_context,
        export_backup_service=ExportBackupService(connection, database_path=database_path),
        backup_restore_service=BackupRestoreService(),
        import_service=ImportService(connection, database_path=database_path),
        database_path=database_path,
        connection=connection,
    )
    window.show()

    return int(app.exec())


if __name__ == "__main__":
    raise SystemExit(main())

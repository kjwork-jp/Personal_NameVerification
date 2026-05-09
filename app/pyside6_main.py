"""PySide6 formal entrypoint for NameVerification v3."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> int:
    """Launch the minimal PySide6 application shell."""
    from PySide6.QtWidgets import QApplication, QDialog

    from app.application.backup_restore_services import BackupRestoreService
    from app.application.core_services import CoreService
    from app.application.enhanced_query_services import EnhancedQueryService
    from app.application.export_backup_services import ExportBackupService
    from app.application.import_services import ImportService
    from app.infrastructure.db import initialize_database
    from app.ui.login_dialog import LoginDialog
    from app.ui.main_window import MainWindow

    database_path = Path(os.environ.get("NAMEVERIFICATION_DB_PATH", "nameverification.db"))
    connection = initialize_database(database_path)
    query_service = EnhancedQueryService(connection)
    core_service = CoreService(connection)

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
        export_backup_service=ExportBackupService(connection),
        backup_restore_service=BackupRestoreService(),
        import_service=ImportService(connection),
        database_path=database_path,
        connection=connection,
    )
    window.show()

    return int(app.exec())


if __name__ == "__main__":
    raise SystemExit(main())

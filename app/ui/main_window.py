"""Main window for NameVerification v3."""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QTabWidget

from app.application.backup_restore_services import BackupRestoreService
from app.application.core_services import CoreService
from app.application.export_backup_services import ExportBackupService
from app.application.import_services import ImportService
from app.application.query_services import QueryService
from app.ui.audit_log_tab import AuditLogTab
from app.ui.link_management_tab import LinkManagementTab
from app.ui.name_management_tab import NameManagementTab
from app.ui.operations_tab import OperationsTab
from app.ui.role_context import RoleContext
from app.ui.search_tab import SearchTab
from app.ui.subtitle_management_tab import SubtitleManagementTab
from app.ui.title_management_tab import TitleManagementTab
from app.ui.trash_tab import TrashTab
from app.ui.ui_style import apply_friendly_theme


class MainWindow(QMainWindow):
    """Top-level main window with user-facing tab layout."""

    def __init__(
        self,
        query_service: QueryService,
        core_service: CoreService,
        role_context: RoleContext | None = None,
        export_backup_service: ExportBackupService | None = None,
        backup_restore_service: BackupRestoreService | None = None,
        import_service: ImportService | None = None,
    ) -> None:
        super().__init__()
        self.setWindowTitle("NameVerification v3")
        self.resize(1180, 760)
        apply_friendly_theme(self)

        tabs = QTabWidget(self)
        active_role = role_context or RoleContext.admin()
        tabs.addTab(SearchTab(query_service=query_service, role_context=active_role), "検索")
        tabs.addTab(
            NameManagementTab(
                core_service=core_service,
                query_service=query_service,
                role_context=active_role,
            ),
            "名前を管理",
        )
        tabs.addTab(
            TitleManagementTab(
                core_service=core_service,
                query_service=query_service,
                role_context=active_role,
            ),
            "タイトルを管理",
        )
        tabs.addTab(
            SubtitleManagementTab(
                core_service=core_service,
                query_service=query_service,
                role_context=active_role,
            ),
            "サブタイトルを管理",
        )
        tabs.addTab(
            LinkManagementTab(
                core_service=core_service,
                query_service=query_service,
                role_context=active_role,
            ),
            "関連付け",
        )
        tabs.addTab(
            TrashTab(
                core_service=core_service,
                query_service=query_service,
                role_context=active_role,
            ),
            "削除データ",
        )
        tabs.addTab(
            AuditLogTab(query_service=query_service, role_context=active_role),
            "操作履歴",
        )
        if (
            export_backup_service is not None
            and backup_restore_service is not None
            and import_service is not None
        ):
            tabs.addTab(
                OperationsTab(
                    export_backup_service=export_backup_service,
                    backup_restore_service=backup_restore_service,
                    import_service=import_service,
                    role_context=active_role,
                ),
                "データ入出力",
            )
        self.setCentralWidget(tabs)

"""Main window for NameVerification v3."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QTabWidget

from app.application.backup_restore_services import BackupRestoreService
from app.application.core_services import CoreService
from app.application.export_backup_services import ExportBackupService
from app.application.import_services import ImportService
from app.application.query_services import QueryService
from app.ui.audit_log_tab import AuditLogTab
from app.ui.help_settings_tab import HelpSettingsTab
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
        database_path: Path | None = None,
        connection: sqlite3.Connection | None = None,
    ) -> None:
        super().__init__()
        self._connection = connection
        self.setWindowTitle("NameVerification v3")
        self.resize(1180, 760)
        apply_friendly_theme(self)

        self.tabs = QTabWidget(self)
        active_role = role_context or RoleContext.admin()
        self._tabs_by_name: dict[str, object] = {}
        self._add_tab(SearchTab(query_service=query_service, role_context=active_role), "検索")
        self._add_tab(
            NameManagementTab(
                core_service=core_service,
                query_service=query_service,
                role_context=active_role,
            ),
            "名前を管理",
        )
        self._add_tab(
            TitleManagementTab(
                core_service=core_service,
                query_service=query_service,
                role_context=active_role,
            ),
            "タイトルを管理",
        )
        self._add_tab(
            SubtitleManagementTab(
                core_service=core_service,
                query_service=query_service,
                role_context=active_role,
            ),
            "サブタイトルを管理",
        )
        self._add_tab(
            LinkManagementTab(
                core_service=core_service,
                query_service=query_service,
                role_context=active_role,
            ),
            "関連付け",
        )
        self._add_tab(
            TrashTab(
                core_service=core_service,
                query_service=query_service,
                role_context=active_role,
            ),
            "削除データ",
        )
        self._add_tab(
            AuditLogTab(query_service=query_service, role_context=active_role),
            "操作履歴",
        )
        if (
            export_backup_service is not None
            and backup_restore_service is not None
            and import_service is not None
        ):
            self._add_tab(
                OperationsTab(
                    export_backup_service=export_backup_service,
                    backup_restore_service=backup_restore_service,
                    import_service=import_service,
                    role_context=active_role,
                ),
                "データ入出力",
            )
        self._add_tab(HelpSettingsTab(database_path=database_path), "ヘルプ / 設定")
        self.tabs.currentChanged.connect(self._refresh_current_tab)
        self.setCentralWidget(self.tabs)

    def _add_tab(self, widget: object, title: str) -> None:
        self.tabs.addTab(widget, title)
        self._tabs_by_name[title] = widget

    def _refresh_current_tab(self) -> None:
        widget = self.tabs.currentWidget()
        if widget is None:
            return
        for method_name in (
            "refresh",
            "_refresh_all",
            "_refresh_list",
            "_on_search_clicked",
            "_reload",
        ):
            method = getattr(widget, method_name, None)
            if callable(method):
                method()
                return
        editor = getattr(widget, "editor", None)
        if editor is not None:
            method = getattr(editor, "_refresh_titles", None)
            if callable(method):
                method()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        if self._connection is not None:
            self._connection.commit()
            self._connection.close()
        super().closeEvent(event)

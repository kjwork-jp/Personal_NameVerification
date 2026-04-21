"""Main window for NameVerification v3."""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QTabWidget

from app.application.core_services import CoreService
from app.application.query_services import QueryService
from app.ui.audit_log_tab import AuditLogTab
from app.ui.link_management_tab import LinkManagementTab
from app.ui.name_management_tab import NameManagementTab
from app.ui.role_context import RoleContext
from app.ui.search_tab import SearchTab
from app.ui.title_subtitle_management_tab import TitleSubtitleManagementTab
from app.ui.trash_tab import TrashTab


class MainWindow(QMainWindow):
    """Top-level main window with minimal tab layout."""

    def __init__(
        self,
        query_service: QueryService,
        core_service: CoreService,
        role_context: RoleContext | None = None,
    ) -> None:
        super().__init__()
        self.setWindowTitle("NameVerification v3")
        self.resize(1080, 720)

        tabs = QTabWidget(self)
        active_role = role_context or RoleContext.admin()
        tabs.addTab(SearchTab(query_service=query_service, role_context=active_role), "検索/照合")
        tabs.addTab(
            NameManagementTab(
                core_service=core_service,
                query_service=query_service,
                role_context=active_role,
            ),
            "名前管理",
        )
        tabs.addTab(
            TitleSubtitleManagementTab(
                core_service=core_service,
                query_service=query_service,
                role_context=active_role,
            ),
            "タイトル/サブタイトル管理",
        )
        tabs.addTab(
            LinkManagementTab(
                core_service=core_service,
                query_service=query_service,
                role_context=active_role,
            ),
            "リンク管理",
        )
        tabs.addTab(
            TrashTab(
                core_service=core_service,
                query_service=query_service,
                role_context=active_role,
            ),
            "ゴミ箱",
        )
        tabs.addTab(
            AuditLogTab(query_service=query_service, role_context=active_role),
            "監査ログ",
        )
        self.setCentralWidget(tabs)

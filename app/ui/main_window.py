"""Main window for NameVerification v3."""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QTabWidget

from app.application.core_services import CoreService
from app.application.query_services import QueryService
from app.ui.name_management_tab import NameManagementTab
from app.ui.search_tab import SearchTab
from app.ui.title_subtitle_management_tab import TitleSubtitleManagementTab


class MainWindow(QMainWindow):
    """Top-level main window with minimal tab layout."""

    def __init__(self, query_service: QueryService, core_service: CoreService) -> None:
        super().__init__()
        self.setWindowTitle("NameVerification v3")
        self.resize(1080, 720)

        tabs = QTabWidget(self)
        tabs.addTab(SearchTab(query_service=query_service), "検索/照合")
        tabs.addTab(
            NameManagementTab(core_service=core_service, query_service=query_service),
            "名前管理",
        )
        tabs.addTab(
            TitleSubtitleManagementTab(core_service=core_service, query_service=query_service),
            "タイトル/サブタイトル管理",
        )
        self.setCentralWidget(tabs)

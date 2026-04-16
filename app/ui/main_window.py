"""Main window for NameVerification v3."""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QTabWidget

from app.application.query_services import QueryService
from app.ui.search_tab import SearchTab


class MainWindow(QMainWindow):
    """Top-level main window with minimal tab layout."""

    def __init__(self, query_service: QueryService) -> None:
        super().__init__()
        self.setWindowTitle("NameVerification v3")
        self.resize(960, 640)

        tabs = QTabWidget(self)
        tabs.addTab(SearchTab(query_service=query_service), "検索/照合")
        self.setCentralWidget(tabs)

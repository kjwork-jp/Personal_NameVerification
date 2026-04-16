"""Presentation layer package (PySide6 UI components)."""

from .audit_log_tab import AuditLogTab
from .link_management_tab import LinkManagementTab
from .main_window import MainWindow
from .name_management_tab import NameManagementTab
from .search_tab import SearchTab
from .title_subtitle_management_tab import TitleSubtitleManagementTab
from .trash_tab import TrashTab

__all__ = [
    "MainWindow",
    "SearchTab",
    "NameManagementTab",
    "TitleSubtitleManagementTab",
    "LinkManagementTab",
    "TrashTab",
    "AuditLogTab",
]

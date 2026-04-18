"""Presentation layer package (PySide6 UI components)."""

from .audit_log_tab import AuditLogTab
from .dialogs import confirm_destructive_action
from .link_management_tab import LinkManagementTab
from .main_window import MainWindow
from .name_management_tab import NameManagementTab
from .permissions import can_create_or_update, can_link, can_run_destructive_actions, can_unlink
from .relation_types import RELATION_TYPE_OPTIONS, RelationTypeOption
from .role_context import RoleContext, UserRole
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
    "confirm_destructive_action",
    "RoleContext",
    "UserRole",
    "can_create_or_update",
    "can_run_destructive_actions",
    "can_link",
    "can_unlink",
    "RelationTypeOption",
    "RELATION_TYPE_OPTIONS",
]

"""Presentation layer package (PySide6 UI components).

The package intentionally keeps imports lazy.  Several modules under ``app.ui`` are
small, non-widget helpers that are useful in headless test and scripting
environments, while the widget modules require the Qt shared libraries to be
available.  Importing those widgets eagerly from this package initializer makes a
simple helper import such as ``app.ui.datetime_display`` fail before the helper
module can be loaded when the host lacks GUI libraries.
"""

from __future__ import annotations

from typing import Any

_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "MainWindow": ("app.ui.main_window", "MainWindow"),
    "SearchTab": ("app.ui.search_tab", "SearchTab"),
    "NameManagementTab": ("app.ui.name_management_tab", "NameManagementTab"),
    "OperationsTab": ("app.ui.operations_tab", "OperationsTab"),
    "HelpSettingsTab": ("app.ui.help_settings_tab", "HelpSettingsTab"),
    "TitleManagementTab": ("app.ui.title_management_tab", "TitleManagementTab"),
    "SubtitleManagementTab": ("app.ui.subtitle_management_tab", "SubtitleManagementTab"),
    "TitleSubtitleManagementTab": (
        "app.ui.title_subtitle_management_tab",
        "TitleSubtitleManagementTab",
    ),
    "LinkManagementTab": ("app.ui.link_management_tab", "LinkManagementTab"),
    "TrashTab": ("app.ui.trash_tab", "TrashTab"),
    "AuditLogTab": ("app.ui.audit_log_tab", "AuditLogTab"),
    "confirm_destructive_action": ("app.ui.dialogs", "confirm_destructive_action"),
    "RoleContext": ("app.ui.role_context", "RoleContext"),
    "UserRole": ("app.ui.role_context", "UserRole"),
    "can_create_or_update": ("app.ui.permissions", "can_create_or_update"),
    "can_run_destructive_actions": (
        "app.ui.permissions",
        "can_run_destructive_actions",
    ),
    "can_link": ("app.ui.permissions", "can_link"),
    "can_unlink": ("app.ui.permissions", "can_unlink"),
    "RelationTypeOption": ("app.ui.relation_types", "RelationTypeOption"),
    "RELATION_TYPE_OPTIONS": ("app.ui.relation_types", "RELATION_TYPE_OPTIONS"),
    "install_title_subtitle_summary_counters": (
        "app.ui.title_subtitle_summary_patch",
        "install_title_subtitle_summary_counters",
    ),
}

__all__ = list(_LAZY_EXPORTS)


def __getattr__(name: str) -> Any:
    """Load package-level UI exports only when requested."""

    try:
        module_name, attribute_name = _LAZY_EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc

    from importlib import import_module

    module = import_module(module_name)
    value = getattr(module, attribute_name)

    if name == "TitleSubtitleManagementTab":
        from app.ui.title_subtitle_summary_patch import install_title_subtitle_summary_counters

        install_title_subtitle_summary_counters()

    globals()[name] = value
    return value

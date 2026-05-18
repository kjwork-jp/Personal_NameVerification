"""UI-level RBAC hardening helpers.

These helpers complement service-layer authorization. They intentionally
operate on widget attributes because several legacy tabs predate the current
RoleContext-based design and need consistent UI hardening without large
behavioral rewrites in one step.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QWidget

from app.ui.role_context import RoleContext

_VIEWER_TOOLTIP = "viewerは参照専用です。この操作は実行できません。"
_EDITOR_DESTRUCTIVE_TOOLTIP = (
    "editorは通常出力/バックアップのみ可能です。復元・取込はadmin専用です。"
)


def _set_enabled(widget: QWidget | None, enabled: bool, tooltip: str | None = None) -> None:
    if widget is None:
        return
    widget.setEnabled(enabled)
    if tooltip is not None:
        widget.setToolTip(tooltip)


def _get(tab: Any, name: str) -> QWidget | None:
    value = getattr(tab, name, None)
    return value if isinstance(value, QWidget) else None


def apply_operations_tab_role_guards(tab: Any, role_context: RoleContext) -> None:
    """Apply strict UI RBAC to the data I/O operations tab.

    Policy:
    - viewer: log viewing only. No export, backup, restore, import, path edits,
      browse buttons, or recent-path deletion.
    - editor: export/backup only. Restore/import and their path controls are disabled.
    - admin: all controls remain available, subject to busy state and internal guards.
    """

    role = role_context.role
    can_export_backup = role in {"editor", "admin"}
    can_restore_import = role == "admin"
    can_clear_history = role in {"editor", "admin"}

    export_backup_fields = (
        "csv_export_path_input",
        "json_export_path_input",
        "sql_dump_path_input",
        "db_path_input",
        "backup_output_path_input",
    )
    restore_import_fields = (
        "restore_backup_path_input",
        "restore_target_db_path_input",
        "import_csv_dir_input",
        "import_json_path_input",
    )
    export_backup_browse_buttons = (
        "csv_export_browse_button",
        "json_export_browse_button",
        "sql_dump_browse_button",
        "db_path_browse_button",
        "backup_output_browse_button",
    )
    restore_import_browse_buttons = (
        "restore_backup_browse_button",
        "restore_target_browse_button",
        "import_csv_dir_browse_button",
        "import_json_browse_button",
    )
    export_backup_action_buttons = (
        "export_csv_button",
        "export_json_button",
        "export_sql_dump_button",
        "create_backup_button",
    )
    restore_import_action_buttons = (
        "restore_button",
        "import_csv_button",
        "import_json_button",
    )

    for name in export_backup_fields + export_backup_browse_buttons + export_backup_action_buttons:
        _set_enabled(
            _get(tab, name),
            can_export_backup,
            None if can_export_backup else _VIEWER_TOOLTIP,
        )
    restore_import_widgets = (
        restore_import_fields + restore_import_browse_buttons + restore_import_action_buttons
    )
    for name in restore_import_widgets:
        _set_enabled(
            _get(tab, name),
            can_restore_import,
            None
            if can_restore_import
            else (_VIEWER_TOOLTIP if role == "viewer" else _EDITOR_DESTRUCTIVE_TOOLTIP),
        )

    _set_enabled(
        _get(tab, "clear_recent_paths_button"),
        can_clear_history,
        None if can_clear_history else _VIEWER_TOOLTIP,
    )
    clear_history_buttons = getattr(tab, "_clear_history_buttons", {})
    if isinstance(clear_history_buttons, dict):
        for button in clear_history_buttons.values():
            if isinstance(button, QWidget):
                _set_enabled(
                    button,
                    can_clear_history,
                    None if can_clear_history else _VIEWER_TOOLTIP,
                )

    # Log viewing remains available for all roles, but exporting logs is treated
    # as an output action and is therefore disallowed for viewer.
    _set_enabled(
        _get(tab, "export_logs_button"),
        role in {"editor", "admin"},
        None if role in {"editor", "admin"} else _VIEWER_TOOLTIP,
    )

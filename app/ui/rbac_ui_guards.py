"""UI-level RBAC hardening helpers.

These helpers complement service-layer authorization. They intentionally
operate on widget attributes because several legacy tabs predate the current
RoleContext-based design and need consistent UI hardening without large
behavioral rewrites in one step.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from PySide6.QtWidgets import QFormLayout, QLabel, QLayout, QTabWidget, QWidget

from app.ui.permissions import (
    can_create_or_update,
    can_link,
    can_run_destructive_actions,
    can_unlink,
)
from app.ui.role_context import RoleContext

_VIEWER_TOOLTIP = "viewerは参照専用です。この操作は実行できません。"
_EDITOR_DESTRUCTIVE_TOOLTIP = (
    "editorは通常出力/バックアップのみ可能です。復元・取込はadmin専用です。"
)
_VIEWER_OPERATIONS_TAB_TOOLTIP = "viewerは実行ログ参照のみ可能です。"

_WRITE_ACTION_BUTTON_NAMES = (
    "create_button",
    "update_button",
    "title_create_button",
    "title_update_button",
    "subtitle_create_button",
    "subtitle_update_button",
)
_DESTRUCTIVE_ACTION_BUTTON_NAMES = (
    "delete_button",
    "restore_button",
    "hard_delete_button",
    "title_delete_button",
    "title_restore_button",
    "title_hard_delete_button",
    "subtitle_delete_button",
    "subtitle_restore_button",
    "subtitle_hard_delete_button",
)
_LINK_ACTION_BUTTON_NAMES = ("link_button",)
_UNLINK_ACTION_BUTTON_NAMES = ("unlink_button",)


def _set_enabled(widget: QWidget | None, enabled: bool, tooltip: str | None = None) -> None:
    if widget is None:
        return
    widget.setEnabled(enabled)
    if tooltip is not None:
        widget.setToolTip(tooltip)


def _set_visible(widget: QWidget | None, visible: bool) -> None:
    if widget is None:
        return
    if visible and widget.parentWidget() is None:
        return
    widget.setVisible(visible)


def _get(tab: Any, name: str) -> QWidget | None:
    value = getattr(tab, name, None)
    return value if isinstance(value, QWidget) else None


def _set_field_visible(tab: Any, name: str, visible: bool) -> None:
    widget = _get(tab, name)
    if widget is None:
        return
    _set_visible(widget, visible)
    label = _find_form_label_for_field(tab, widget)
    _set_visible(label, visible)


def _find_form_label_for_field(tab: Any, field: QWidget) -> QWidget | None:
    if not isinstance(tab, QWidget):
        return None
    layout = tab.layout()
    if layout is None:
        return None
    return _find_form_label_in_layout(layout, field, set())


def _find_form_label_in_layout(
    layout: QLayout,
    field: QWidget,
    seen_layout_ids: set[int],
) -> QWidget | None:
    if id(layout) in seen_layout_ids:
        return None
    seen_layout_ids.add(id(layout))

    if isinstance(layout, QFormLayout):
        label = layout.labelForField(field)
        if isinstance(label, QWidget):
            return label

    for index in range(layout.count()):
        item = layout.itemAt(index)
        if item is None:
            continue
        child_layout = item.layout()
        if child_layout is not None:
            label = _find_form_label_in_layout(child_layout, field, seen_layout_ids)
            if label is not None:
                return label
        child_widget = item.widget()
        if child_widget is None:
            continue
        nested_layout = child_widget.layout()
        if nested_layout is not None:
            label = _find_form_label_in_layout(nested_layout, field, seen_layout_ids)
            if label is not None:
                return label
    return None


def _set_info_message(tab: Any, message: str) -> None:
    label = getattr(tab, "message_label", None)
    if not isinstance(label, QLabel):
        return
    label.setStyleSheet("color: #7dd3fc;")
    label.setText(message)


def apply_tab_action_visibility_guards(tab: Any, role_context: RoleContext) -> None:
    """Hide action buttons and subtabs that the current role can never execute.

    Disabled buttons are still useful for transient states, such as no row
    selected. Buttons that are permanently unavailable for a role are hidden to
    reduce visual noise and prevent the UI from looking broken.
    """

    can_write = can_create_or_update(role_context.role)
    can_destructive = can_run_destructive_actions(role_context.role)
    for target in _iter_role_guard_targets(tab):
        _set_buttons_visible(target, _WRITE_ACTION_BUTTON_NAMES, can_write)
        _set_buttons_visible(target, _DESTRUCTIVE_ACTION_BUTTON_NAMES, can_destructive)
        _set_buttons_visible(target, _LINK_ACTION_BUTTON_NAMES, can_link(role_context.role))
        _set_buttons_visible(target, _UNLINK_ACTION_BUTTON_NAMES, can_unlink(role_context.role))
        _apply_readonly_layout_guards(target, role_context)
        _apply_link_subtab_role_guards(target, role_context)


def _iter_role_guard_targets(root: Any) -> Iterator[Any]:
    seen: set[int] = set()
    pending = [root]
    while pending:
        target = pending.pop()
        if target is None or id(target) in seen:
            continue
        seen.add(id(target))
        yield target
        for attr_name in ("editor", "title_tab", "subtitle_tab"):
            child = getattr(target, attr_name, None)
            if child is not None:
                pending.append(child)


def _set_buttons_visible(target: Any, names: tuple[str, ...], visible: bool) -> None:
    for name in names:
        _set_visible(_get(target, name), visible)


def _apply_readonly_layout_guards(tab: Any, role_context: RoleContext) -> None:
    role = role_context.role
    can_write = can_create_or_update(role)
    can_destructive = can_run_destructive_actions(role)

    # NameManagementTab: keep search/filter/list visible, hide edit-only fields for viewer.
    if _get(tab, "names_table") is not None and _get(tab, "raw_name_input") is not None:
        for field_name in ("operator_input", "raw_name_input", "note_input"):
            _set_field_visible(tab, field_name, can_write or can_destructive)
        if not can_write:
            _set_info_message(tab, "viewerは参照専用です。名前一覧のみ確認できます。")

    # TitleSubtitleManagementTab: keep selector/tables visible, hide edit forms for viewer.
    if _get(tab, "titles_table") is not None and _get(tab, "title_name_input") is not None:
        for field_name in (
            "title_name_input",
            "title_note_input",
            "title_link_name_combo",
            "title_link_names_list",
            "subtitle_code_input",
            "subtitle_name_input",
            "subtitle_sort_order_input",
            "subtitle_note_input",
        ):
            _set_field_visible(tab, field_name, can_write)
        if not can_write:
            _set_info_message(
                tab,
                "viewerは参照専用です。タイトル/サブタイトル一覧のみ確認できます。",
            )

    # LinkManagementTab: if no registration/removal operation is available, show only guidance.
    if (
        _get(tab, "register_name_combo") is not None
        and _get(tab, "unregister_name_combo") is not None
    ):
        can_register = can_link(role)
        can_remove = can_unlink(role)
        link_tabs = getattr(tab, "tabs", None)
        if isinstance(link_tabs, QTabWidget):
            _set_visible(link_tabs, can_register or can_remove)
        if not can_register and not can_remove:
            _set_info_message(
                tab,
                "viewerは参照専用です。関連付けの登録・解除フォームは表示しません。",
            )

    # TrashTab: non-admin can inspect deleted rows only; hide mutation identity/actions.
    if _get(tab, "list_table") is not None and _get(tab, "entity_selector") is not None:
        _set_field_visible(tab, "operator_input", can_destructive)
        if not can_destructive:
            _set_info_message(tab, "このロールでは削除済みデータを参照のみできます。")


def _apply_link_subtab_role_guards(tab: Any, role_context: RoleContext) -> None:
    sub_tabs = getattr(tab, "tabs", None)
    if not isinstance(sub_tabs, QTabWidget):
        return
    if _get(tab, "register_name_combo") is None or _get(tab, "unregister_name_combo") is None:
        return

    enabled_by_title = {
        "登録": can_link(role_context.role),
        "解除": can_unlink(role_context.role),
    }
    first_visible_enabled_index: int | None = None
    current_visible_enabled = True
    tab_bar = sub_tabs.tabBar()
    set_tab_visible = getattr(tab_bar, "setTabVisible", None)
    for index in range(sub_tabs.count()):
        title = sub_tabs.tabText(index)
        visible = enabled_by_title.get(title, True)
        sub_tabs.setTabEnabled(index, visible)
        if callable(set_tab_visible):
            set_tab_visible(index, visible)
        if visible and first_visible_enabled_index is None:
            first_visible_enabled_index = index
        if index == sub_tabs.currentIndex():
            current_visible_enabled = visible
    if not current_visible_enabled and first_visible_enabled_index is not None:
        sub_tabs.setCurrentIndex(first_visible_enabled_index)


def apply_operations_tab_role_guards(tab: Any, role_context: RoleContext) -> None:
    """Apply strict UI RBAC to the data I/O operations tab.

    Policy:
    - viewer: log viewing only. Unavailable operation groups are hidden rather
      than merely disabled.
    - editor: export/backup only. Restore/import are hidden.
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

    _install_cancel_visibility_guard(tab)

    clear_recent_paths_button = _get(tab, "clear_recent_paths_button")
    _set_enabled(
        clear_recent_paths_button,
        can_clear_history,
        None if can_clear_history else _VIEWER_TOOLTIP,
    )
    _set_visible(clear_recent_paths_button, can_clear_history)
    clear_history_buttons = getattr(tab, "_clear_history_buttons", {})
    if isinstance(clear_history_buttons, dict):
        for button in clear_history_buttons.values():
            if isinstance(button, QWidget):
                _set_enabled(
                    button,
                    can_clear_history,
                    None if can_clear_history else _VIEWER_TOOLTIP,
                )
                button.setVisible(can_clear_history)

    # Log viewing remains available for all roles, but exporting logs is treated
    # as an output action and is therefore hidden for viewer.
    export_logs_button = _get(tab, "export_logs_button")
    can_export_logs = role in {"editor", "admin"}
    _set_enabled(
        export_logs_button,
        can_export_logs,
        None if can_export_logs else _VIEWER_TOOLTIP,
    )
    _set_visible(export_logs_button, can_export_logs)
    _apply_operations_subtab_role_guards(tab, role_context)


def _install_cancel_visibility_guard(tab: Any) -> None:
    """Show the cancel button only while an async operation is running."""

    cancel_button = _get(tab, "cancel_operation_button")
    original_apply_busy_state = getattr(tab, "_apply_busy_state", None)
    if cancel_button is None or not callable(original_apply_busy_state):
        return
    if getattr(tab, "_cancel_visibility_guard_installed", False) is True:
        _set_visible(cancel_button, bool(getattr(tab, "_is_busy", False)))
        return

    def _guarded_apply_busy_state() -> None:
        original_apply_busy_state()
        _set_visible(cancel_button, bool(getattr(tab, "_is_busy", False)))

    tab._apply_busy_state = _guarded_apply_busy_state
    tab._cancel_visibility_guard_installed = True
    _guarded_apply_busy_state()


def _apply_operations_subtab_role_guards(tab: Any, role_context: RoleContext) -> None:
    sub_tabs = getattr(tab, "operations_subtabs", None)
    if not isinstance(sub_tabs, QTabWidget):
        return

    role = role_context.role
    enabled_by_title = {
        "ガイド": True,
        "Export": role in {"editor", "admin"},
        "Backup": role in {"editor", "admin"},
        "Restore": role == "admin",
        "Import": role == "admin",
        "Operations Log": True,
    }
    tooltip_by_title = {
        "Export": _VIEWER_OPERATIONS_TAB_TOOLTIP,
        "Backup": _VIEWER_OPERATIONS_TAB_TOOLTIP,
        "Restore": _VIEWER_TOOLTIP if role == "viewer" else _EDITOR_DESTRUCTIVE_TOOLTIP,
        "Import": _VIEWER_TOOLTIP if role == "viewer" else _EDITOR_DESTRUCTIVE_TOOLTIP,
    }

    first_visible_enabled_index: int | None = None
    current_visible_enabled = True
    tab_bar = sub_tabs.tabBar()
    set_tab_visible = getattr(tab_bar, "setTabVisible", None)
    for index in range(sub_tabs.count()):
        title = sub_tabs.tabText(index)
        enabled = enabled_by_title.get(title, True)
        visible = enabled
        sub_tabs.setTabEnabled(index, enabled)
        if callable(set_tab_visible):
            set_tab_visible(index, visible)
        sub_tabs.setTabToolTip(index, "" if enabled else tooltip_by_title.get(title, ""))
        if visible and enabled and first_visible_enabled_index is None:
            first_visible_enabled_index = index
        if index == sub_tabs.currentIndex():
            current_visible_enabled = visible and enabled

    if not current_visible_enabled and first_visible_enabled_index is not None:
        sub_tabs.setCurrentIndex(first_visible_enabled_index)

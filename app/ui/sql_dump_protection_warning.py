"""Protection warning for full SQL dump export."""

from __future__ import annotations

from types import MethodType
from typing import Any

SQL_DUMP_PROTECTION_WARNING = (
    "SQL dump はfull DB dumpです。users table、password_hash、password_salt等の"
    "認証関連フィールドを含む可能性があるため、保護対象ファイルとして扱い、"
    "共有・添付・外部保存時はアクセス制御を確認してください。"
)


def apply_sql_dump_protection_warning(operations_tab: Any) -> None:
    """Make SQL dump protection requirements visible in the Operations UI."""

    if getattr(operations_tab, "_sql_dump_protection_warning_applied", False):
        return

    button = getattr(operations_tab, "export_sql_dump_button", None)
    if button is not None and hasattr(button, "setToolTip"):
        button.setToolTip(SQL_DUMP_PROTECTION_WARNING)

    line_edit = getattr(operations_tab, "sql_dump_path_input", None)
    if line_edit is not None and hasattr(line_edit, "setToolTip"):
        line_edit.setToolTip(SQL_DUMP_PROTECTION_WARNING)

    original_run_export_sql_dump = operations_tab._run_export_sql_dump

    def _guarded_run_export_sql_dump(self: Any) -> None:
        self._set_message(SQL_DUMP_PROTECTION_WARNING)
        original_run_export_sql_dump()

    operations_tab._run_export_sql_dump = MethodType(
        _guarded_run_export_sql_dump,
        operations_tab,
    )
    operations_tab._sql_dump_protection_warning_applied = True

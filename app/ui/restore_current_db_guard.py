"""Guard Data I/O restore from replacing the currently opened database."""

from __future__ import annotations

import os
from pathlib import Path
from types import MethodType
from typing import Any, Callable


def apply_restore_current_db_guard(
    operations_tab: Any,
    current_database_path: Path | None,
) -> None:
    """Block GUI restore when the target is the active application DB.

    The current SQLite connection may keep the DB file locked on Windows.  Rather
    than attempting an in-process file replacement, stop before the destructive
    confirmation dialog and before the restore service is called.
    """

    if current_database_path is None:
        return
    if getattr(operations_tab, "_restore_current_db_guard_applied", False):
        return

    current_db_key = _normalize_path_key(current_database_path)
    original_run_restore: Callable[[], None] = operations_tab._run_restore

    def _guarded_run_restore(self: Any) -> None:
        if not self._ensure_not_busy():
            return
        backup_path = self._require_text(
            self.restore_backup_path_input,
            "バックアップ入力ファイル",
        )
        target_path = self._require_text(
            self.restore_target_db_path_input,
            "復元先DBファイル",
        )
        if backup_path is None or target_path is None:
            return
        if _normalize_path_key(Path(target_path)) == current_db_key:
            message = (
                "Restore blocked: 現在利用中DBはアプリ起動中にGUI復元できません。"
                "アプリを終了してoffline restore手順で復元してください。"
            )
            self._set_message(message, is_error=True)
            self._record_operation(
                "restore",
                "error",
                message,
                path=backup_path,
                path2=target_path,
            )
            return
        original_run_restore()

    operations_tab._run_restore = MethodType(_guarded_run_restore, operations_tab)
    operations_tab._restore_current_db_guard_applied = True


def _normalize_path_key(path: Path) -> str:
    return os.path.normcase(str(path.expanduser().resolve(strict=False)))

"""Small OperationsTab behavior fixes."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def apply_operations_test_fixes() -> None:
    from app.ui import operations_tab as module

    cls = module.OperationsTab
    cls._run_export_csv = _run_export_csv
    cls._run_export_json = _run_export_json
    cls._run_restore = _run_restore
    cls._run_import_json = _run_import_json
    cls._reload_operation_logs = _reload_logs
    cls._reset_log_page_and_reload = _reset_logs


def _busy(self: Any) -> bool:
    if self._is_busy:
        self._set_message("実行中です。完了まで待ってください。", is_error=True)
        return True
    return False


def _start(self: Any, action: str, label: str, work: Any, path: str | None = None) -> None:
    if _busy(self):
        return
    self._is_busy = True
    self._cancel_requested = False
    self._apply_busy_state()
    self._set_message(f"{label} 実行中...")

    def ok(result: Any) -> None:
        message = f"{label} 成功: {result}"
        status = "cancel" if self._cancel_requested else "success"
        prefix = "[CANCEL]" if self._cancel_requested else "[OK]"
        self._set_message(f"{prefix} {message}")
        self._record_operation(action, status, message, path=path)
        self._reload_operation_logs()

    def ng(error: BaseException) -> None:
        message = f"{label} 失敗: {error}"
        self._set_message(f"[ERROR] {message}", is_error=True)
        self._record_operation(action, "error", message, path=path)
        self._reload_operation_logs()

    def done() -> None:
        self._is_busy = False
        self._hide_progress()
        self._apply_busy_state()

    self._show_progress(label)
    self._operation_executor.submit(work, ok, ng, done)


def _text(self: Any, widget: Any, label: str) -> str | None:
    value = widget.text().strip()
    if not value:
        self._set_message(f"[ERROR] {label} は必須です", is_error=True)
        return None
    return value


def _run_export_csv(self: Any) -> None:
    path = _text(self, self.csv_export_path_input, "CSV出力先ディレクトリ")
    if path is None or _busy(self):
        return
    self._push_recent_path("csv_export_dir", path)
    _start(
        self,
        "export_csv",
        "CSV export",
        lambda: self._export_backup_service.export_csv(Path(path), role=self._role),
        path,
    )


def _run_export_json(self: Any) -> None:
    if _busy(self):
        return
    path = _text(self, self.json_export_path_input, "JSON出力先ファイル")
    if path is None:
        return
    self._push_recent_path("json_export_file", path)
    _start(
        self,
        "export_json",
        "JSON export",
        lambda: self._export_backup_service.export_json(Path(path), role=self._role),
        path,
    )


def _run_restore(self: Any) -> None:
    from app.ui import operations_tab as module

    if _busy(self):
        return
    backup = _text(self, self.restore_backup_path_input, "バックアップ入力ファイル")
    target = _text(self, self.restore_target_db_path_input, "復元先DBファイル")
    if backup is None or target is None:
        return
    if not module.confirm_destructive_action(self, "復元の確認", "復元を実行します。"):
        self._set_message("restore をキャンセルしました")
        return
    _start(
        self,
        "restore",
        "Restore",
        lambda: self._backup_restore_service.restore_database(Path(backup), Path(target), role=self._role),
        backup,
    )


def _run_import_json(self: Any) -> None:
    from app.ui import operations_tab as module

    if _busy(self):
        return
    path = _text(self, self.import_json_path_input, "JSONファイル")
    if path is None:
        return
    if not module.confirm_destructive_action(self, "JSON取込の確認", "JSON取込を実行します。"):
        self._set_message("import_json をキャンセルしました")
        self._record_operation("import_json", "cancel", "import_json をキャンセルしました", path=path)
        return
    _start(
        self,
        "import_json",
        "JSON import",
        lambda: self._import_service.import_json(Path(path), role=self._role),
        path,
    )


def _reset_logs(self: Any) -> None:
    self._log_page_index = 0
    self._reload_operation_logs()


def _reload_logs(self: Any) -> None:
    include_archives = self.include_archives_checkbox.isChecked()
    events, _decode_errors = self._operation_logger.read_latest(
        self._log_page_size() * 20,
        include_archives=include_archives,
    )
    rows = _filter(self, list(events))
    if not rows:
        self.operation_log_view.setPlainText("ログはまだありません。")
        return
    lines = []
    for event in rows:
        lines.append(
            f"{event.timestamp} | {event.action} | {event.role} | {event.status} | {event.message}"
        )
    self.operation_log_view.setPlainText("\n".join(lines))


def _filter(self: Any, rows: list[Any]) -> list[Any]:
    pattern = self.log_message_search_input.text().strip()
    if not pattern:
        return rows
    if not self.log_regex_checkbox.isChecked():
        return [row for row in rows if pattern.lower() in _event_text(row).lower()]
    flags = 0
    if self.log_regex_ignore_case_checkbox.isChecked():
        flags |= re.IGNORECASE
    if self.log_regex_multiline_checkbox.isChecked():
        flags |= re.MULTILINE
    if self.log_regex_dotall_checkbox.isChecked():
        flags |= re.DOTALL
    try:
        regex = re.compile(pattern, flags)
    except re.error as exc:
        self.operation_log_view.setPlainText(f"regex エラー: {exc}")
        return []
    return [row for row in rows if regex.search(_event_text(row))]


def _event_text(row: Any) -> str:
    return "\n".join(
        str(value or "")
        for value in [row.action, row.status, row.message, row.path, row.path2]
    )

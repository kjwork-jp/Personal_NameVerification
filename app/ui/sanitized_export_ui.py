"""UI hook for sanitized sharing-oriented JSON export."""

from __future__ import annotations

from pathlib import Path
from types import MethodType
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from PySide6.QtWidgets import QPushButton

SANITIZED_EXPORT_TOOLTIP = (
    "共有用JSONを出力します。業務データのみを許可リスト方式で出力し、"
    "ユーザー管理・認証・監査・設定などの管理系テーブルは含めません。"
)


def apply_sanitized_export_ui(operations_tab: Any) -> None:
    """Add a sanitized JSON export action to the Operations tab."""

    if getattr(operations_tab, "_sanitized_export_ui_applied", False):
        return

    button_factory = type(operations_tab.export_json_button)
    button = button_factory("共有用JSON出力")
    button.setToolTip(SANITIZED_EXPORT_TOOLTIP)
    button.setMinimumHeight(24)
    operations_tab.export_sanitized_json_button = button

    _insert_button_near_json_export(operations_tab, button)
    operations_tab._run_export_sanitized_json = MethodType(
        _run_export_sanitized_json,
        operations_tab,
    )
    button.clicked.connect(operations_tab._run_export_sanitized_json)
    operations_tab._sanitized_export_ui_applied = True


def _insert_button_near_json_export(
    operations_tab: Any,
    button: QPushButton,
) -> None:
    parent = operations_tab.export_json_button.parentWidget()
    if parent is None or parent.layout() is None:
        operations_tab.layout().addWidget(button)
        return

    group_layout = parent.layout()
    for index in range(group_layout.count()):
        item = group_layout.itemAt(index)
        row_layout = item.layout()
        if row_layout is None:
            continue
        for row_index in range(row_layout.count()):
            row_item = row_layout.itemAt(row_index)
            if row_item.widget() is operations_tab.export_json_button:
                row_layout.insertWidget(row_index + 1, button)
                return
    group_layout.addWidget(button)


def _run_export_sanitized_json(self: Any) -> None:
    if not self._ensure_not_busy():
        return
    path = self._require_text(self.json_export_path_input, "共有用JSON出力先ファイル")
    if path is None:
        return

    def _work() -> object:
        return self._export_backup_service.export_sanitized_json(Path(path), role=self._role)

    def _success(result: object) -> None:
        output_path = cast(Path, result)
        self._push_recent_path("json_export_file", path)
        status = "cancel" if self._cancel_requested else "success"
        message = (
            "共有用JSON export 完了（cancel requested 後に完了）"
            if self._cancel_requested
            else f"共有用JSON export 成功: {output_path}"
        )
        self._set_message(message)
        self._record_operation("export_sanitized_json", status, message, path=path)

    def _error(exc: Exception) -> None:
        message = f"共有用JSON export 失敗: {exc}"
        self._set_message(message, is_error=True)
        self._record_operation("export_sanitized_json", "error", message, path=path)

    self._start_async_operation(
        "export_sanitized_json",
        "共有用JSON export",
        _work,
        _success,
        _error,
    )

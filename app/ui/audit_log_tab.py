"""Operation history tab UI (read-only)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.application.read_models import ChangeLogRow
from app.ui.public_id_display import short_public_id
from app.ui.role_context import RoleContext, UserRole
from app.ui.ui_style import PageHeader, compact_layout, set_status_message


class AuditLogReadService(Protocol):
    def list_change_logs(
        self,
        role: UserRole = "admin",
        *,
        entity_type: str | None = None,
        action: str | None = None,
        operator_id: str | None = None,
        created_from: str | None = None,
        created_to: str | None = None,
        limit: int = 200,
    ) -> list[ChangeLogRow]: ...


@dataclass(frozen=True)
class _FilterValues:
    entity_type: str | None
    action: str | None
    operator_id: str | None
    created_from: str | None
    created_to: str | None
    limit: int


class AuditLogTab(QWidget):
    """Read-only UI for browsing operation history."""

    def __init__(
        self, query_service: AuditLogReadService, role_context: RoleContext | None = None
    ) -> None:
        super().__init__()
        self._query_service = query_service
        self._role_context = role_context or RoleContext.admin()
        self._rows: list[ChangeLogRow] = []

        self.entity_type_input = QLineEdit()
        self.entity_type_input.setPlaceholderText("例: names / titles / subtitles")

        self.action_input = QLineEdit()
        self.action_input.setPlaceholderText("例: create / update / delete")

        self.operator_id_input = QLineEdit()
        self.operator_id_input.setPlaceholderText("操作者")

        self.created_from_input = QLineEdit()
        self.created_from_input.setPlaceholderText("開始日時（例: 2026-01-01T00:00:00Z）")

        self.created_to_input = QLineEdit()
        self.created_to_input.setPlaceholderText("終了日時（例: 2026-01-31T23:59:59Z）")

        self.limit_input = QLineEdit("200")
        self.limit_input.setPlaceholderText("表示件数")

        self.message_label = QLabel("")

        self.reload_button = QPushButton("一覧を更新")
        self.reload_button.clicked.connect(self._reload)

        self.logs_table = QTableWidget(0, 6)
        self.logs_table.setHorizontalHeaderLabels(
            ["内部ID", "公開ID", "データ種類", "内部対象ID", "実行した操作", "実行日時"]
        )
        self.logs_table.setColumnHidden(0, True)
        self.logs_table.setColumnHidden(3, True)
        self.logs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.logs_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.logs_table.itemSelectionChanged.connect(self._on_selected)

        self.detail_summary_label = QLabel("選択中の操作: 未選択")

        self.before_json_view = QTextEdit()
        self.before_json_view.setReadOnly(True)
        self.before_json_view.setPlaceholderText("変更前の内容")

        self.after_json_view = QTextEdit()
        self.after_json_view.setReadOnly(True)
        self.after_json_view.setPlaceholderText("変更後の内容")

        self.diff_view = QTextEdit()
        self.diff_view.setReadOnly(True)
        self.diff_view.setPlaceholderText("変更差分")

        form = QFormLayout()
        compact_layout(form, margins=2, spacing=3)
        form.addRow("データの種類", self.entity_type_input)
        form.addRow("実行した操作", self.action_input)
        form.addRow("操作者", self.operator_id_input)
        form.addRow("開始日時", self.created_from_input)
        form.addRow("終了日時", self.created_to_input)
        form.addRow("表示件数", self.limit_input)

        actions = QHBoxLayout()
        compact_layout(actions, margins=0, spacing=4)
        actions.addWidget(self.reload_button)

        detail_panel = QWidget()
        detail_layout = QVBoxLayout(detail_panel)
        compact_layout(detail_layout, margins=3, spacing=4)
        detail_layout.addWidget(self.detail_summary_label)
        detail_layout.addWidget(QLabel("変更差分"))
        detail_layout.addWidget(self.diff_view, 2)
        detail_layout.addWidget(QLabel("変更前の内容"))
        detail_layout.addWidget(self.before_json_view, 1)
        detail_layout.addWidget(QLabel("変更後の内容"))
        detail_layout.addWidget(self.after_json_view, 1)

        splitter = QSplitter()
        splitter.addWidget(self.logs_table)
        splitter.addWidget(detail_panel)
        splitter.setSizes([520, 620])

        root = QVBoxLayout(self)
        compact_layout(root, margins=5, spacing=4)
        root.addWidget(
            PageHeader(
                "操作履歴",
                "登録・更新・削除など、誰がいつ何を変更したかを確認する画面です。"
                "変更内容は項目名付きで表示します。",
            )
        )
        root.addLayout(form)
        root.addLayout(actions)
        root.addWidget(self.message_label)
        root.addWidget(splitter, 1)

        self._reload()

    def _reload(self) -> None:
        try:
            filters = self._collect_filters()
            self._rows = self._query_service.list_change_logs(
                role=self._role_context.role,
                entity_type=filters.entity_type,
                action=filters.action,
                operator_id=filters.operator_id,
                created_from=filters.created_from,
                created_to=filters.created_to,
                limit=filters.limit,
            )
        except ValueError as exc:
            self._set_message(f"入力エラー: {exc}", is_error=True)
            return
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"読込に失敗しました: {exc}", is_error=True)
            return

        self.logs_table.setRowCount(len(self._rows))
        for i, row in enumerate(self._rows):
            self.logs_table.setItem(i, 0, QTableWidgetItem(str(row.id)))
            public_id_item = QTableWidgetItem(short_public_id(row.public_id))
            public_id_item.setToolTip(f"操作履歴公開ID={row.public_id or '未採番'}")
            self.logs_table.setItem(i, 1, public_id_item)
            self.logs_table.setItem(i, 2, QTableWidgetItem(row.entity_type))
            self.logs_table.setItem(i, 3, QTableWidgetItem(str(row.entity_id)))
            self.logs_table.setItem(i, 4, QTableWidgetItem(row.action))
            self.logs_table.setItem(i, 5, QTableWidgetItem(row.created_at))

        self.detail_summary_label.setText("選択中の操作: 未選択")
        self.before_json_view.clear()
        self.after_json_view.clear()
        self.diff_view.clear()

        if self._rows:
            self.logs_table.selectRow(0)
            self._on_selected()
            self._set_message(f"{len(self._rows)} 件を表示")
        else:
            self._set_message("表示対象の操作履歴がありません", level="warning")

    def _collect_filters(self) -> _FilterValues:
        limit_raw = self.limit_input.text().strip() or "200"
        limit = int(limit_raw)
        if limit <= 0:
            raise ValueError("表示件数は 1 以上で入力してください")

        return _FilterValues(
            entity_type=_optional(self.entity_type_input.text()),
            action=_optional(self.action_input.text()),
            operator_id=_optional(self.operator_id_input.text()),
            created_from=_optional(self.created_from_input.text()),
            created_to=_optional(self.created_to_input.text()),
            limit=limit,
        )

    def _on_selected(self) -> None:
        idx = self.logs_table.currentRow()
        if idx < 0 or idx >= len(self._rows):
            self.detail_summary_label.setText("選択中の操作: 未選択")
            self.before_json_view.clear()
            self.after_json_view.clear()
            self.diff_view.clear()
            return

        row = self._rows[idx]
        before = _parse_json_object(row.before_json)
        after = _parse_json_object(row.after_json)
        self.detail_summary_label.setText(
            f"操作: {row.action} / データ種類: {row.entity_type} / "
            f"公開ID: {row.public_id or '未採番'} / 内部対象ID: {row.entity_id} / "
            f"操作者: {row.operator_id} / 実行日時: {row.created_at}"
        )
        self.before_json_view.setPlainText(_format_json_like(row.before_json, before))
        self.after_json_view.setPlainText(_format_json_like(row.after_json, after))
        self.diff_view.setPlainText(_format_diff(before, after))

    def _set_message(
        self, message: str, *, is_error: bool = False, level: str | None = None
    ) -> None:
        if level is None:
            level = "error" if is_error else "success"
        set_status_message(self.message_label, message, level=level)


def _optional(value: str) -> str | None:
    stripped = value.strip()
    return stripped if stripped else None


def _parse_json_object(value: str | None) -> dict[str, Any] | None:
    if not value:
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _format_json_like(raw_value: str | None, parsed: dict[str, Any] | None) -> str:
    if not raw_value:
        return "（なし）"
    if parsed is None:
        return raw_value
    return "\n".join(f"{key}: {_format_value(parsed[key])}" for key in sorted(parsed))


def _format_diff(
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
) -> str:
    if before is None and after is None:
        return "変更差分を解析できません。変更前/変更後の内容を確認してください。"
    before = before or {}
    after = after or {}
    keys = sorted(set(before) | set(after))
    if not keys:
        return "差分はありません。"
    lines: list[str] = []
    for key in keys:
        before_value = before.get(key, "（なし）")
        after_value = after.get(key, "（なし）")
        marker = "=" if before_value == after_value else "→"
        lines.append(
            f"{key}: {_format_value(before_value)} {marker} {_format_value(after_value)}"
        )
    return "\n".join(lines)


def _format_value(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)

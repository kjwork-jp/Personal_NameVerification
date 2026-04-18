"""Audit log tab UI (read-only)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

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


class AuditLogReadService(Protocol):
    def list_change_logs(
        self,
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
    """Read-only UI for browsing change logs."""

    def __init__(self, query_service: AuditLogReadService) -> None:
        super().__init__()
        self._query_service = query_service
        self._rows: list[ChangeLogRow] = []

        self.entity_type_input = QLineEdit()
        self.entity_type_input.setPlaceholderText("entity_type (e.g. names)")

        self.action_input = QLineEdit()
        self.action_input.setPlaceholderText("action (e.g. update)")

        self.operator_id_input = QLineEdit()
        self.operator_id_input.setPlaceholderText("operator_id")

        self.created_from_input = QLineEdit()
        self.created_from_input.setPlaceholderText("created_from (ISO8601)")

        self.created_to_input = QLineEdit()
        self.created_to_input.setPlaceholderText("created_to (ISO8601)")

        self.limit_input = QLineEdit("200")
        self.limit_input.setPlaceholderText("limit")

        self.message_label = QLabel("")

        self.reload_button = QPushButton("再読込")
        self.reload_button.clicked.connect(self._reload)

        self.logs_table = QTableWidget(0, 5)
        self.logs_table.setHorizontalHeaderLabels(
            ["ID", "entity_type", "entity_id", "action", "created_at"]
        )
        self.logs_table.itemSelectionChanged.connect(self._on_selected)

        self.detail_summary_label = QLabel("詳細: 未選択")

        self.before_json_view = QTextEdit()
        self.before_json_view.setReadOnly(True)
        self.before_json_view.setPlaceholderText("before_json")

        self.after_json_view = QTextEdit()
        self.after_json_view.setReadOnly(True)
        self.after_json_view.setPlaceholderText("after_json")

        form = QFormLayout()
        form.addRow("entity_type", self.entity_type_input)
        form.addRow("action", self.action_input)
        form.addRow("operator_id", self.operator_id_input)
        form.addRow("created_from", self.created_from_input)
        form.addRow("created_to", self.created_to_input)
        form.addRow("limit", self.limit_input)

        actions = QHBoxLayout()
        actions.addWidget(self.reload_button)

        detail_panel = QWidget()
        detail_layout = QVBoxLayout(detail_panel)
        detail_layout.addWidget(self.detail_summary_label)
        detail_layout.addWidget(QLabel("before_json"))
        detail_layout.addWidget(self.before_json_view)
        detail_layout.addWidget(QLabel("after_json"))
        detail_layout.addWidget(self.after_json_view)

        splitter = QSplitter()
        splitter.addWidget(self.logs_table)
        splitter.addWidget(detail_panel)

        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addLayout(actions)
        root.addWidget(self.message_label)
        root.addWidget(splitter)

        self._reload()

    def _reload(self) -> None:
        try:
            filters = self._collect_filters()
            self._rows = self._query_service.list_change_logs(
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
            self.logs_table.setItem(i, 1, QTableWidgetItem(row.entity_type))
            self.logs_table.setItem(i, 2, QTableWidgetItem(str(row.entity_id)))
            self.logs_table.setItem(i, 3, QTableWidgetItem(row.action))
            self.logs_table.setItem(i, 4, QTableWidgetItem(row.created_at))

        self.detail_summary_label.setText("詳細: 未選択")
        self.before_json_view.clear()
        self.after_json_view.clear()

        if self._rows:
            self.logs_table.selectRow(0)
            self._set_message(f"{len(self._rows)} 件を表示")
        else:
            self._set_message("表示対象の監査ログがありません")

    def _collect_filters(self) -> _FilterValues:
        limit_raw = self.limit_input.text().strip() or "200"
        limit = int(limit_raw)
        if limit <= 0:
            raise ValueError("limit は 1 以上で入力してください")

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
            self.detail_summary_label.setText("詳細: 未選択")
            self.before_json_view.clear()
            self.after_json_view.clear()
            return

        row = self._rows[idx]
        self.detail_summary_label.setText(
            f"詳細: id={row.id}, type={row.entity_type}, action={row.action}, "
            f"operator={row.operator_id}, created_at={row.created_at}"
        )
        self.before_json_view.setPlainText(row.before_json or "")
        self.after_json_view.setPlainText(row.after_json or "")

    def _set_message(self, message: str, *, is_error: bool = False) -> None:
        color = "#b00020" if is_error else "#1b5e20"
        self.message_label.setStyleSheet(f"color: {color};")
        self.message_label.setText(message)


def _optional(value: str) -> str | None:
    stripped = value.strip()
    return stripped if stripped else None

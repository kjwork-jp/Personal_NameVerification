"""Admin-only user audit log tab."""

from __future__ import annotations

import json
from typing import Any

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.application.read_models import UserAuditLogRow
from app.application.user_audit_services import UserAuditLogService
from app.domain.errors import AuthorizationError
from app.ui.role_context import RoleContext
from app.ui.ui_style import PageHeader, compact_layout, make_combo_searchable, set_status_message

_ACTION_OPTIONS = [
    "all",
    "login_success",
    "login_failure",
    "user_create",
    "user_disable",
    "user_enable",
    "user_role_change",
    "password_change",
    "password_reset",
    "lockout",
    "setup_admin_create",
]


class UserAuditLogTab(QWidget):
    """Read-only admin UI for user_audit_logs."""

    def __init__(
        self,
        user_audit_service: UserAuditLogService,
        role_context: RoleContext,
    ) -> None:
        super().__init__()
        self._user_audit_service = user_audit_service
        self._role_context = role_context
        self._rows: list[UserAuditLogRow] = []

        self.status_label = QLabel()
        set_status_message(self.status_label, "ユーザー監査ログを読み込みます。", level="info")

        self.actor_input = QLineEdit()
        self.actor_input.setPlaceholderText("実行者")
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("対象ユーザー")
        self.action_input = QComboBox()
        self.action_input.addItems(_ACTION_OPTIONS)
        make_combo_searchable(self.action_input)
        self.limit_input = QSpinBox()
        self.limit_input.setRange(1, 10000)
        self.limit_input.setValue(200)
        self.limit_input.setSingleStep(50)
        self.reload_button = QPushButton("一覧を更新")
        self.reload_button.clicked.connect(self.refresh)

        form = QFormLayout()
        compact_layout(form, margins=2, spacing=3)
        form.addRow("実行者", self.actor_input)
        form.addRow("対象ユーザー", self.target_input)
        form.addRow("操作", self.action_input)
        form.addRow("表示件数", self.limit_input)

        actions = QHBoxLayout()
        compact_layout(actions, margins=0, spacing=4)
        actions.addWidget(self.reload_button)

        self.logs_table = QTableWidget(0, 5)
        self.logs_table.setHorizontalHeaderLabels(
            ["内部ID", "実行者", "対象ユーザー", "操作", "実行日時"]
        )
        self.logs_table.setColumnHidden(0, True)
        self.logs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.logs_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.logs_table.itemSelectionChanged.connect(self._on_selected)

        self.detail_summary_label = QLabel("選択中の監査ログ: 未選択")
        self.before_json_view = QTextEdit()
        self.before_json_view.setReadOnly(True)
        self.before_json_view.setPlaceholderText("変更前")
        self.after_json_view = QTextEdit()
        self.after_json_view.setReadOnly(True)
        self.after_json_view.setPlaceholderText("変更後")
        self.diff_view = QTextEdit()
        self.diff_view.setReadOnly(True)
        self.diff_view.setPlaceholderText("差分")

        detail_panel = QWidget()
        detail_layout = QVBoxLayout(detail_panel)
        compact_layout(detail_layout, margins=3, spacing=4)
        detail_layout.addWidget(self.detail_summary_label)
        detail_layout.addWidget(QLabel("差分"))
        detail_layout.addWidget(self.diff_view, 2)
        detail_layout.addWidget(QLabel("変更前"))
        detail_layout.addWidget(self.before_json_view, 1)
        detail_layout.addWidget(QLabel("変更後"))
        detail_layout.addWidget(self.after_json_view, 1)

        splitter = QSplitter()
        splitter.addWidget(self.logs_table)
        splitter.addWidget(detail_panel)
        splitter.setSizes([520, 620])

        root = QVBoxLayout(self)
        compact_layout(root, margins=5, spacing=4)
        root.addWidget(
            PageHeader(
                "ユーザー監査ログ",
                "ログイン成功/失敗、ユーザー作成、権限変更、無効化/有効化をadminが確認する画面です。",
            )
        )
        root.addLayout(form)
        root.addLayout(actions)
        root.addWidget(self.status_label)
        root.addWidget(splitter, 1)

        self.refresh()

    def refresh(self) -> None:
        if self._role_context.role != "admin":
            set_status_message(self.status_label, "ユーザー監査ログはadmin専用です。", level="warning")
            return
        try:
            self._rows = self._user_audit_service.list_user_audit_logs(
                role=self._role_context.role,
                actor_operator_id=_optional(self.actor_input.text()),
                target_operator_id=_optional(self.target_input.text()),
                action=_combo_optional(self.action_input),
                limit=self.limit_input.value(),
            )
        except AuthorizationError as exc:
            set_status_message(self.status_label, str(exc), level="error")
            return
        except Exception as exc:  # noqa: BLE001
            set_status_message(self.status_label, f"読込に失敗しました: {exc}", level="error")
            return

        self.logs_table.setRowCount(len(self._rows))
        for i, row in enumerate(self._rows):
            self.logs_table.setItem(i, 0, QTableWidgetItem(str(row.id)))
            self.logs_table.setItem(i, 1, QTableWidgetItem(row.actor_operator_id))
            self.logs_table.setItem(i, 2, QTableWidgetItem(row.target_operator_id or ""))
            self.logs_table.setItem(i, 3, QTableWidgetItem(row.action))
            self.logs_table.setItem(i, 4, QTableWidgetItem(row.created_at))

        self.detail_summary_label.setText("選択中の監査ログ: 未選択")
        self.before_json_view.clear()
        self.after_json_view.clear()
        self.diff_view.clear()

        if self._rows:
            self.logs_table.selectRow(0)
            self._on_selected()
            set_status_message(self.status_label, f"{len(self._rows)} 件を表示", level="success")
        else:
            set_status_message(self.status_label, "表示対象のユーザー監査ログがありません。", level="warning")

    def _on_selected(self) -> None:
        idx = self.logs_table.currentRow()
        if idx < 0 or idx >= len(self._rows):
            self.detail_summary_label.setText("選択中の監査ログ: 未選択")
            self.before_json_view.clear()
            self.after_json_view.clear()
            self.diff_view.clear()
            return

        row = self._rows[idx]
        before = _parse_json_object(row.before_json)
        after = _parse_json_object(row.after_json)
        self.detail_summary_label.setText(
            f"#{row.id} / {row.action} / actor={row.actor_operator_id} / target={row.target_operator_id or '-'}"
        )
        self.before_json_view.setPlainText(_pretty_json(before))
        self.after_json_view.setPlainText(_pretty_json(after))
        self.diff_view.setPlainText(_diff_text(before, after))


def _combo_optional(combo: QComboBox) -> str | None:
    text = combo.currentText().strip()
    if text == "" or text == "all":
        return None
    return text


def _optional(value: str) -> str | None:
    stripped = value.strip()
    if stripped == "":
        return None
    return stripped


def _parse_json_object(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {"_raw": value}
    if isinstance(parsed, dict):
        return parsed
    return {"_value": parsed}


def _pretty_json(value: dict[str, Any]) -> str:
    if not value:
        return ""
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def _diff_text(before: dict[str, Any], after: dict[str, Any]) -> str:
    keys = sorted(set(before) | set(after))
    lines: list[str] = []
    for key in keys:
        before_value = before.get(key)
        after_value = after.get(key)
        if before_value != after_value:
            lines.append(f"{key}: {before_value!r} -> {after_value!r}")
    return "\n".join(lines)

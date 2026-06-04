"""Operation history tab UI (read-only)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateTimeEdit,
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

from app.application.read_models import ChangeLogRow
from app.ui.datetime_display import format_datetime_display
from app.ui.public_id_display import short_public_id
from app.ui.role_context import RoleContext, UserRole
from app.ui.ui_style import (
    PageHeader,
    apply_readable_table,
    compact_layout,
    make_combo_searchable,
    set_status_message,
)

ENTITY_TYPE_OPTIONS = [
    "all",
    "names",
    "titles",
    "subtitles",
    "name_title_links",
    "name_subtitle_links",
]
ACTION_OPTIONS = ["all", "create", "update", "delete", "restore", "link", "unlink"]


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

        self.entity_type_input = QComboBox()
        self.entity_type_input.addItems(ENTITY_TYPE_OPTIONS)
        make_combo_searchable(self.entity_type_input)

        self.action_input = QComboBox()
        self.action_input.addItems(ACTION_OPTIONS)
        make_combo_searchable(self.action_input)

        self.operator_id_input = QLineEdit()
        self.operator_id_input.setPlaceholderText("操作者")

        self.created_from_enabled = QCheckBox("開始日時を使う")
        self.created_from_input = QDateTimeEdit()
        self.created_from_input.setCalendarPopup(True)
        self.created_from_input.setDisplayFormat("yyyy/MM/dd HH:mm:ss")
        self.created_from_input.setDateTime(QDateTime.currentDateTime().addDays(-7))
        self.created_from_input.setEnabled(False)
        self.created_from_enabled.stateChanged.connect(
            lambda *_: self.created_from_input.setEnabled(
                self.created_from_enabled.isChecked()
            )
        )

        self.created_to_enabled = QCheckBox("終了日時を使う")
        self.created_to_input = QDateTimeEdit()
        self.created_to_input.setCalendarPopup(True)
        self.created_to_input.setDisplayFormat("yyyy/MM/dd HH:mm:ss")
        self.created_to_input.setDateTime(QDateTime.currentDateTime())
        self.created_to_input.setEnabled(False)
        self.created_to_enabled.stateChanged.connect(
            lambda *_: self.created_to_input.setEnabled(self.created_to_enabled.isChecked())
        )

        self.limit_input = QSpinBox()
        self.limit_input.setRange(1, 10000)
        self.limit_input.setValue(200)
        self.limit_input.setSingleStep(50)

        self.audit_export_path_input = QLineEdit("audit_logs_review.json")
        self.audit_export_path_input.setToolTip(
            "現在表示中の操作履歴だけをレビュー証跡JSONとして出力します。"
        )

        self.message_label = QLabel("")

        self.reload_button = QPushButton("一覧を更新")
        self.reload_button.clicked.connect(self._reload)
        self.export_visible_rows_button = QPushButton("表示中履歴JSON出力")
        self.export_visible_rows_button.clicked.connect(self._export_visible_rows_json)

        self.logs_table = QTableWidget(0, 6)
        self.logs_table.setHorizontalHeaderLabels(
            ["内部ID", "公開ID", "データ種類", "内部対象ID", "実行した操作", "実行日時"]
        )
        self.logs_table.setColumnHidden(0, True)
        self.logs_table.setColumnHidden(3, True)
        apply_readable_table(self.logs_table)
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
        form.addRow(self.created_from_enabled, self.created_from_input)
        form.addRow(self.created_to_enabled, self.created_to_input)
        form.addRow("表示件数", self.limit_input)
        form.addRow("レビューJSON出力先", self.audit_export_path_input)

        actions = QHBoxLayout()
        compact_layout(actions, margins=0, spacing=4)
        actions.addWidget(self.reload_button)
        actions.addWidget(self.export_visible_rows_button)

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
                "データの種類・操作は検索可能なプルダウン、日時はカレンダーで絞り込めます。",
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
            self.logs_table.setItem(i, 5, QTableWidgetItem(_created_at_display(row)))

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
        return _FilterValues(
            entity_type=_combo_optional(self.entity_type_input),
            action=_combo_optional(self.action_input),
            operator_id=_optional(self.operator_id_input.text()),
            created_from=_optional_datetime(
                self.created_from_input,
                enabled=self.created_from_enabled.isChecked(),
            ),
            created_to=_optional_datetime(
                self.created_to_input,
                enabled=self.created_to_enabled.isChecked(),
            ),
            limit=self.limit_input.value(),
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
            f"操作者: {row.operator_id} / 実行日時: {_created_at_display(row)}"
        )
        self.before_json_view.setPlainText(_format_json_like(row.before_json, before))
        self.after_json_view.setPlainText(_format_json_like(row.after_json, after))
        self.diff_view.setPlainText(_format_diff(before, after))

    def _export_visible_rows_json(self) -> None:
        output_text = self.audit_export_path_input.text().strip()
        if not output_text:
            self._set_message("レビューJSON出力先を入力してください", is_error=True)
            return
        try:
            output_path = self._write_visible_rows_json(Path(output_text))
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"操作履歴JSON出力に失敗しました: {exc}", is_error=True)
            return
        self._set_message(f"表示中の操作履歴をJSON出力しました: {output_path}")

    def _write_visible_rows_json(self, output_path: Path) -> Path:
        resolved = output_path.expanduser().resolve(strict=False)
        if resolved.exists() and resolved.is_dir():
            raise ValueError(f"出力先がフォルダです: {resolved}")
        resolved.parent.mkdir(parents=True, exist_ok=True)
        filters = self._collect_filters()
        payload = {
            "export_type": "audit_log_review",
            "row_count": len(self._rows),
            "filters": {
                "entity_type": filters.entity_type,
                "action": filters.action,
                "operator_id": filters.operator_id,
                "created_from": filters.created_from,
                "created_to": filters.created_to,
                "limit": filters.limit,
            },
            "rows": [_row_export_payload(row) for row in self._rows],
        }
        resolved.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return resolved

    def _set_message(
        self, message: str, *, is_error: bool = False, level: str | None = None
    ) -> None:
        if level is None:
            level = "error" if is_error else "success"
        set_status_message(self.message_label, message, level=level)


def _optional(value: str) -> str | None:
    stripped = value.strip()
    return stripped if stripped else None


def _combo_optional(combo: QComboBox) -> str | None:
    value = combo.currentText().strip()
    return None if not value or value == "all" else value


def _optional_datetime(widget: QDateTimeEdit, *, enabled: bool) -> str | None:
    if not enabled:
        return None
    return widget.dateTime().toUTC().toString("yyyy-MM-ddTHH:mm:ssZ")


def _created_at_display(row: ChangeLogRow) -> str:
    return format_datetime_display(row.created_at, fallback="不明")


def _parse_json_object(value: str | None) -> dict[str, Any] | None:
    if not value:
        return None
    try:
        data = json.loads(value)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _format_json_like(value: str | None, parsed: dict[str, Any] | None) -> str:
    if parsed is None:
        return value or ""
    return json.dumps(parsed, ensure_ascii=False, indent=2, sort_keys=True)


def _format_diff(
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
) -> str:
    if before is None and after is None:
        return ""
    before = before or {}
    after = after or {}
    keys = sorted(set(before) | set(after))
    lines: list[str] = []
    for key in keys:
        before_value = before.get(key)
        after_value = after.get(key)
        if before_value != after_value:
            lines.append(f"{key}: {before_value!r} -> {after_value!r}")
    return "\n".join(lines) if lines else "差分なし"


def _row_export_payload(row: ChangeLogRow) -> dict[str, Any]:
    return {
        "id": row.id,
        "public_id": row.public_id,
        "entity_type": row.entity_type,
        "entity_id": row.entity_id,
        "action": row.action,
        "operator_id": row.operator_id,
        "created_at": row.created_at,
        "before_json": row.before_json,
        "after_json": row.after_json,
    }

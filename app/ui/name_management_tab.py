"""Name management tab UI (name entity only)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.application.core_services import NameInput
from app.application.read_models import NameDetail, NameSearchRow
from app.ui.dialogs import confirm_destructive_action
from app.ui.permissions import can_create_or_update, can_run_destructive_actions
from app.ui.role_context import RoleContext, UserRole


class NameWriteService(Protocol):
    def create_name(
        self, payload: NameInput, operator_id: str, role: UserRole = "admin"
    ) -> int: ...

    def update_name(
        self, name_id: int, payload: NameInput, operator_id: str, role: UserRole = "admin"
    ) -> None: ...

    def delete_name(self, name_id: int, operator_id: str, role: UserRole = "admin") -> None: ...

    def restore_name(self, name_id: int, operator_id: str, role: UserRole = "admin") -> None: ...

    def hard_delete_name(
        self, name_id: int, operator_id: str, role: UserRole = "admin"
    ) -> None: ...


class NameReadService(Protocol):
    def search_names(
        self,
        query: str | None = None,
        role: UserRole = "admin",
        *,
        exact_match: bool = False,
        title_id: int | None = None,
        has_links: bool | None = None,
        include_deleted: bool = False,
    ) -> list[NameSearchRow]: ...

    def get_name_detail(self, name_id: int, role: UserRole = "admin") -> NameDetail: ...


@dataclass(frozen=True)
class _SelectedName:
    id: int
    deleted: bool


class NameManagementTab(QWidget):
    """UI for name create/update/delete/restore/hard-delete flows."""

    def __init__(
        self,
        core_service: NameWriteService,
        query_service: NameReadService,
        role_context: RoleContext | None = None,
    ) -> None:
        super().__init__()
        self._core_service = core_service
        self._query_service = query_service
        self._role_context = role_context or RoleContext.admin()
        self._rows: list[NameSearchRow] = []
        self._selected: _SelectedName | None = None

        self.operator_input = QLineEdit()
        self.operator_input.setPlaceholderText("操作者ID")
        self.operator_input.setToolTip("operator_id が必要です")

        self.raw_name_input = QLineEdit()
        self.raw_name_input.setPlaceholderText("表示名")
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("備考")

        self.message_label = QLabel("")

        self.names_table = QTableWidget(0, 4)
        self.names_table.setHorizontalHeaderLabels(["ID", "名前", "状態", "紐づき数"])
        self.names_table.itemSelectionChanged.connect(self._on_row_selected)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)

        self.refresh_button = QPushButton("再読込")
        self.refresh_button.clicked.connect(self._refresh_list)

        self.create_button = QPushButton("新規作成")
        self.create_button.clicked.connect(self._create_name)

        self.update_button = QPushButton("更新")
        self.update_button.clicked.connect(self._update_name)

        self.delete_button = QPushButton("論理削除")
        self.delete_button.clicked.connect(self._delete_name)

        self.restore_button = QPushButton("復元")
        self.restore_button.clicked.connect(self._restore_name)

        self.hard_delete_button = QPushButton("完全削除")
        self.hard_delete_button.clicked.connect(self._hard_delete_name)

        form = QFormLayout()
        form.addRow("操作者ID", self.operator_input)
        form.addRow("名前", self.raw_name_input)
        form.addRow("備考", self.note_input)

        actions = QHBoxLayout()
        for button in [
            self.refresh_button,
            self.create_button,
            self.update_button,
            self.delete_button,
            self.restore_button,
            self.hard_delete_button,
        ]:
            actions.addWidget(button)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(actions)
        layout.addWidget(self.message_label)
        layout.addWidget(self.names_table)
        layout.addWidget(QLabel("詳細"))
        layout.addWidget(self.detail_text)

        self._apply_role_guards()
        self._refresh_list()

    def _apply_role_guards(self) -> None:
        role = self._role_context.role
        can_write = can_create_or_update(role)
        can_destructive = can_run_destructive_actions(role)

        self.create_button.setEnabled(can_write)
        self.update_button.setEnabled(can_write)
        self.delete_button.setEnabled(can_destructive)
        self.restore_button.setEnabled(can_destructive)
        self.hard_delete_button.setEnabled(can_destructive)

        self.create_button.setToolTip(
            "このロールでは実行できません" if not can_write else "operator_id を入力して実行します"
        )
        self.update_button.setToolTip(
            "このロールでは実行できません"
            if not can_write
            else "行が選択されていない場合は実行できません"
        )
        self.delete_button.setToolTip(
            "このロールでは実行できません"
            if not can_destructive
            else "行が選択されていない場合は実行できません"
        )
        self.restore_button.setToolTip(
            "このロールでは実行できません"
            if not can_destructive
            else "削除済み行を選択してください"
        )
        self.hard_delete_button.setToolTip(
            "このロールでは実行できません"
            if not can_destructive
            else "削除済み行を選択してください"
        )

    def _refresh_list(self) -> None:
        try:
            rows = self._query_service.search_names(
                include_deleted=True, role=self._role_context.role
            )
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"一覧取得に失敗しました: {exc}", is_error=True)
            return

        self._rows = rows
        self.names_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.names_table.setItem(i, 0, QTableWidgetItem(str(row.id)))
            self.names_table.setItem(i, 1, QTableWidgetItem(row.raw_name))
            self.names_table.setItem(
                i, 2, QTableWidgetItem("削除済み" if row.deleted_at else "有効")
            )
            self.names_table.setItem(i, 3, QTableWidgetItem(str(row.linked_count)))

        self.detail_text.clear()
        self._selected = None
        if rows:
            self.names_table.selectRow(0)

    def _on_row_selected(self) -> None:
        idx = self.names_table.currentRow()
        if idx < 0 or idx >= len(self._rows):
            self._selected = None
            self.detail_text.clear()
            return

        row = self._rows[idx]
        self._selected = _SelectedName(id=row.id, deleted=row.deleted_at is not None)
        self.raw_name_input.setText(row.raw_name)

        try:
            detail = self._query_service.get_name_detail(row.id, role=self._role_context.role)
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"詳細取得に失敗しました: {exc}", is_error=True)
            return

        status = "削除済み" if detail.deleted_at else "有効"
        self.detail_text.setPlainText(
            "\n".join(
                [
                    f"ID: {detail.id}",
                    f"名前: {detail.raw_name}",
                    f"正規化名: {detail.normalized_name}",
                    f"状態: {status}",
                    f"更新日時: {detail.updated_at}",
                    f"備考: {detail.note or ''}",
                ]
            )
        )
        self.note_input.setText(detail.note or "")

    def _create_name(self) -> None:
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールでは新規作成できません", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        try:
            self._core_service.create_name(
                self._current_payload(),
                operator_id=operator_id,
                role=self._role_context.role,
            )
            self._set_message("新規作成しました")
            self._refresh_list()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"新規作成に失敗しました: {exc}", is_error=True)

    def _update_name(self) -> None:
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールでは更新できません", is_error=True)
            return

        selected = self._require_selected()
        if selected is None:
            return
        if selected.deleted:
            self._set_message("削除済みは更新できません", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return

        try:
            self._core_service.update_name(
                selected.id,
                self._current_payload(),
                operator_id=operator_id,
                role=self._role_context.role,
            )
            self._set_message("更新しました")
            self._refresh_list()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"更新に失敗しました: {exc}", is_error=True)

    def _delete_name(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールでは論理削除できません", is_error=True)
            return

        selected = self._require_selected()
        if selected is None:
            return
        if selected.deleted:
            self._set_message("既に削除済みです", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return

        if not confirm_destructive_action(
            self,
            "論理削除の確認",
            f"名前ID={selected.id} を論理削除します。よろしいですか？",
        ):
            self._set_message("論理削除をキャンセルしました")
            return

        try:
            self._core_service.delete_name(
                selected.id, operator_id=operator_id, role=self._role_context.role
            )
            self._set_message("論理削除しました")
            self._refresh_list()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"論理削除に失敗しました: {exc}", is_error=True)

    def _restore_name(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールでは復元できません", is_error=True)
            return

        selected = self._require_selected()
        if selected is None:
            return
        if not selected.deleted:
            self._set_message("有効行は復元できません", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return

        if not confirm_destructive_action(
            self,
            "復元の確認",
            f"名前ID={selected.id} を復元します。よろしいですか？",
        ):
            self._set_message("復元をキャンセルしました")
            return

        try:
            self._core_service.restore_name(
                selected.id, operator_id=operator_id, role=self._role_context.role
            )
            self._set_message("復元しました")
            self._refresh_list()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"復元に失敗しました: {exc}", is_error=True)

    def _hard_delete_name(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールでは完全削除できません", is_error=True)
            return

        selected = self._require_selected()
        if selected is None:
            return
        if not selected.deleted:
            self._set_message("完全削除は削除済み行のみ可能です", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return

        if not confirm_destructive_action(
            self,
            "完全削除の確認",
            f"名前ID={selected.id} を完全削除します。この操作は元に戻せません。",
        ):
            self._set_message("完全削除をキャンセルしました")
            return

        try:
            self._core_service.hard_delete_name(
                selected.id, operator_id=operator_id, role=self._role_context.role
            )
            self._set_message("完全削除しました")
            self._refresh_list()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"完全削除に失敗しました: {exc}", is_error=True)

    def _current_payload(self) -> NameInput:
        return NameInput(raw_name=self.raw_name_input.text(), note=self.note_input.text() or None)

    def _require_operator_id(self) -> str | None:
        operator_id = self.operator_input.text().strip()
        if not operator_id:
            self._set_message("operator_id を入力してください", is_error=True)
            return None
        return operator_id

    def _require_selected(self) -> _SelectedName | None:
        if self._selected is None:
            self._set_message("行を選択してください", is_error=True)
            return None
        return self._selected

    def _set_message(self, message: str, *, is_error: bool = False) -> None:
        color = "#b00020" if is_error else "#0b6b0b"
        self.message_label.setStyleSheet(f"color: {color};")
        self.message_label.setText(message)

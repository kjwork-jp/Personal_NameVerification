"""Trash tab UI for restoring/hard-deleting logically deleted entities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.application.read_models import NameDetail, RelatedRow, SubtitleDetail, TitleDetail
from app.ui.dialogs import confirm_destructive_action
from app.ui.permissions import can_run_destructive_actions
from app.ui.role_context import RoleContext, UserRole


class TrashReadService(Protocol):
    def list_deleted_names(self, role: UserRole = "admin") -> list[NameDetail]: ...
    def list_deleted_titles(self, role: UserRole = "admin") -> list[TitleDetail]: ...
    def list_deleted_subtitles(self, role: UserRole = "admin") -> list[SubtitleDetail]: ...
    def list_deleted_links(self, role: UserRole = "admin") -> list[RelatedRow]: ...


class TrashWriteService(Protocol):
    def restore_name(self, name_id: int, operator_id: str, role: UserRole = "admin") -> None: ...
    def hard_delete_name(self, name_id: int, operator_id: str, role: UserRole = "admin") -> None: ...
    def restore_title(self, title_id: int, operator_id: str, role: UserRole = "admin") -> None: ...
    def hard_delete_title(self, title_id: int, operator_id: str, role: UserRole = "admin") -> None: ...
    def restore_subtitle(self, subtitle_id: int, operator_id: str, role: UserRole = "admin") -> None: ...
    def hard_delete_subtitle(self, subtitle_id: int, operator_id: str, role: UserRole = "admin") -> None: ...
    def restore_link(self, link_id: int, operator_id: str, role: UserRole = "admin") -> None: ...
    def hard_delete_link(self, link_id: int, operator_id: str, role: UserRole = "admin") -> None: ...


@dataclass(frozen=True)
class _Selection:
    entity_id: int
    deleted_at: str | None


class TrashTab(QWidget):
    """Cross-entity trash UI."""

    def __init__(
        self,
        core_service: TrashWriteService,
        query_service: TrashReadService,
        role_context: RoleContext | None = None,
    ) -> None:
        super().__init__()
        self._core_service = core_service
        self._query_service = query_service
        self._role_context = role_context or RoleContext.admin()
        self._names: list[NameDetail] = []
        self._titles: list[TitleDetail] = []
        self._subtitles: list[SubtitleDetail] = []
        self._links: list[RelatedRow] = []
        self._selected: _Selection | None = None

        self.entity_selector = QComboBox()
        self.entity_selector.addItems(["名前", "タイトル", "サブタイトル", "リンク", "Name", "Title", "Subtitle", "Link"])
        self.entity_selector.currentTextChanged.connect(self._reload)
        self.operator_input = QLineEdit()
        self.operator_input.setPlaceholderText("操作者ID")
        self.operator_input.setToolTip("操作者ID が必要です")
        self.message_label = QLabel("")
        self.list_table = QTableWidget(0, 3)
        self.list_table.setHorizontalHeaderLabels(["ID", "表示", "deleted_at"])
        self.list_table.itemSelectionChanged.connect(self._on_selected)
        self.detail_label = QLabel("詳細: 未選択")
        self.reload_button = QPushButton("再読込")
        self.restore_button = QPushButton("復元")
        self.hard_delete_button = QPushButton("完全削除")
        self.reload_button.clicked.connect(self._reload)
        self.restore_button.clicked.connect(self._restore_selected)
        self.hard_delete_button.clicked.connect(self._hard_delete_selected)

        form = QFormLayout()
        form.addRow("対象", self.entity_selector)
        form.addRow("操作者ID", self.operator_input)
        actions = QHBoxLayout()
        actions.addWidget(self.reload_button)
        actions.addWidget(self.restore_button)
        actions.addWidget(self.hard_delete_button)
        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addLayout(actions)
        root.addWidget(self.message_label)
        root.addWidget(self.list_table)
        root.addWidget(self.detail_label)
        self._apply_role_guards()
        self._reload()

    def _entity_key(self) -> str:
        return {
            "名前": "name",
            "Name": "name",
            "タイトル": "title",
            "Title": "title",
            "サブタイトル": "subtitle",
            "Subtitle": "subtitle",
            "リンク": "link",
            "Link": "link",
        }.get(self.entity_selector.currentText(), "name")

    def _apply_role_guards(self) -> None:
        enabled = can_run_destructive_actions(self._role_context.role)
        self.restore_button.setEnabled(enabled)
        self.hard_delete_button.setEnabled(enabled)
        tooltip = "このロールでは実行できません" if not enabled else "削除済みデータを選択してください"
        self.restore_button.setToolTip(tooltip)
        self.hard_delete_button.setToolTip(tooltip)

    def _reload(self) -> None:
        key = self._entity_key()
        self._selected = None
        self.detail_label.setText("詳細: 未選択")
        try:
            if key == "name":
                self._names = self._query_service.list_deleted_names(role=self._role_context.role)
                self._fill_name_rows(self._names)
            elif key == "title":
                self._titles = self._query_service.list_deleted_titles(role=self._role_context.role)
                self._fill_title_rows(self._titles)
            elif key == "subtitle":
                self._subtitles = self._query_service.list_deleted_subtitles(role=self._role_context.role)
                self._fill_subtitle_rows(self._subtitles)
            else:
                self._links = self._query_service.list_deleted_links(role=self._role_context.role)
                self._fill_link_rows(self._links)
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"一覧取得に失敗しました: {exc}", is_error=True)
            return
        if self.list_table.rowCount() > 0:
            self.list_table.selectRow(0)
            self._on_selected()
        else:
            self._set_message("削除済みデータはありません")

    def _fill_name_rows(self, names: list[NameDetail]) -> None:
        self.list_table.setRowCount(len(names))
        for i, row in enumerate(names):
            self.list_table.setItem(i, 0, QTableWidgetItem(str(row.id)))
            self.list_table.setItem(i, 1, QTableWidgetItem(row.raw_name))
            self.list_table.setItem(i, 2, QTableWidgetItem(row.deleted_at or ""))

    def _fill_title_rows(self, titles: list[TitleDetail]) -> None:
        self.list_table.setRowCount(len(titles))
        for i, row in enumerate(titles):
            self.list_table.setItem(i, 0, QTableWidgetItem(str(row.id)))
            self.list_table.setItem(i, 1, QTableWidgetItem(row.title_name))
            self.list_table.setItem(i, 2, QTableWidgetItem(row.deleted_at or ""))

    def _fill_subtitle_rows(self, subtitles: list[SubtitleDetail]) -> None:
        self.list_table.setRowCount(len(subtitles))
        for i, row in enumerate(subtitles):
            self.list_table.setItem(i, 0, QTableWidgetItem(str(row.id)))
            self.list_table.setItem(i, 1, QTableWidgetItem(f"{row.subtitle_code} {row.subtitle_name}"))
            self.list_table.setItem(i, 2, QTableWidgetItem(row.deleted_at or ""))

    def _fill_link_rows(self, links: list[RelatedRow]) -> None:
        self.list_table.setRowCount(len(links))
        for i, row in enumerate(links):
            self.list_table.setItem(i, 0, QTableWidgetItem(str(row.link_id)))
            self.list_table.setItem(i, 1, QTableWidgetItem(f"name={row.name_id} / {row.title_name}:{row.subtitle_code} ({row.relation_type})"))
            self.list_table.setItem(i, 2, QTableWidgetItem(row.link_deleted_at or ""))

    def _on_selected(self) -> None:
        row = self.list_table.currentRow()
        if row < 0:
            self._selected = None
            self.detail_label.setText("詳細: 未選択")
            return
        key = self._entity_key()
        if key == "name" and row < len(self._names):
            item = self._names[row]
            self._selected = _Selection(item.id, item.deleted_at)
            self.detail_label.setText(f"詳細: Name id={item.id} raw={item.raw_name} deleted_at={item.deleted_at}")
        elif key == "title" and row < len(self._titles):
            item = self._titles[row]
            self._selected = _Selection(item.id, item.deleted_at)
            self.detail_label.setText(f"詳細: Title id={item.id} name={item.title_name} deleted_at={item.deleted_at}")
        elif key == "subtitle" and row < len(self._subtitles):
            item = self._subtitles[row]
            self._selected = _Selection(item.id, item.deleted_at)
            self.detail_label.setText(f"詳細: Subtitle id={item.id} code={item.subtitle_code} deleted_at={item.deleted_at}")
        elif key == "link" and row < len(self._links):
            item = self._links[row]
            self._selected = _Selection(item.link_id, item.link_deleted_at)
            self.detail_label.setText(f"詳細: Link id={item.link_id} name_id={item.name_id} subtitle_id={item.subtitle_id} deleted_at={item.link_deleted_at}")

    def _restore_selected(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールでは復元できません", is_error=True)
            return
        operator_id = self._require_operator_id()
        selected = self._require_deleted_selection()
        if operator_id is None or selected is None:
            return
        if not confirm_destructive_action(self, "復元の確認", f"ID={selected.entity_id} を復元します。よろしいですか？"):
            self._set_message("復元をキャンセルしました")
            return
        method = {
            "name": "restore_name",
            "title": "restore_title",
            "subtitle": "restore_subtitle",
            "link": "restore_link",
        }[self._entity_key()]
        getattr(self._core_service, method)(selected.entity_id, operator_id, role=self._role_context.role)
        self._set_message("復元しました")

    def _hard_delete_selected(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールでは完全削除できません", is_error=True)
            return
        operator_id = self._require_operator_id()
        selected = self._require_deleted_selection()
        if operator_id is None or selected is None:
            return
        if not confirm_destructive_action(self, "完全削除の確認", f"ID={selected.entity_id} を完全削除します。この操作は元に戻せません。"):
            self._set_message("完全削除をキャンセルしました")
            return
        method = {
            "name": "hard_delete_name",
            "title": "hard_delete_title",
            "subtitle": "hard_delete_subtitle",
            "link": "hard_delete_link",
        }[self._entity_key()]
        getattr(self._core_service, method)(selected.entity_id, operator_id, role=self._role_context.role)
        self._set_message("完全削除しました")

    def _require_operator_id(self) -> str | None:
        operator_id = self.operator_input.text().strip()
        if not operator_id:
            self._set_message("操作者ID を入力してください", is_error=True)
            return None
        return operator_id

    def _require_deleted_selection(self) -> _Selection | None:
        if self._selected is None:
            self._on_selected()
        if self._selected is None:
            self._set_message("対象を選択してください", is_error=True)
            return None
        if self._selected.deleted_at is None:
            self._set_message("active データには実行できません", is_error=True)
            return None
        return self._selected

    def _set_message(self, message: str, *, is_error: bool = False) -> None:
        color = "#b00020" if is_error else "#1b5e20"
        self.message_label.setStyleSheet(f"color: {color};")
        self.message_label.setText(message)

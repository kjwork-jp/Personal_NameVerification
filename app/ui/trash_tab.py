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
    def list_deleted_names(self) -> list[NameDetail]: ...

    def list_deleted_titles(self) -> list[TitleDetail]: ...

    def list_deleted_subtitles(self) -> list[SubtitleDetail]: ...

    def list_deleted_links(self) -> list[RelatedRow]: ...


class TrashWriteService(Protocol):
    def restore_name(self, name_id: int, operator_id: str, role: UserRole = "admin") -> None: ...

    def hard_delete_name(
        self, name_id: int, operator_id: str, role: UserRole = "admin"
    ) -> None: ...

    def restore_title(self, title_id: int, operator_id: str, role: UserRole = "admin") -> None: ...

    def hard_delete_title(
        self, title_id: int, operator_id: str, role: UserRole = "admin"
    ) -> None: ...

    def restore_subtitle(
        self, subtitle_id: int, operator_id: str, role: UserRole = "admin"
    ) -> None: ...

    def hard_delete_subtitle(
        self, subtitle_id: int, operator_id: str, role: UserRole = "admin"
    ) -> None: ...

    def restore_link(self, link_id: int, operator_id: str, role: UserRole = "admin") -> None: ...

    def hard_delete_link(
        self, link_id: int, operator_id: str, role: UserRole = "admin"
    ) -> None: ...


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
        self.entity_selector.addItems(["Name", "Title", "Subtitle", "Link"])
        self.entity_selector.currentTextChanged.connect(self._reload)

        self.operator_input = QLineEdit()
        self.operator_input.setPlaceholderText("operator_id")
        self.operator_input.setToolTip("operator_id が必要です")

        self.message_label = QLabel("")

        self.list_table = QTableWidget(0, 3)
        self.list_table.setHorizontalHeaderLabels(["ID", "表示", "deleted_at"])
        self.list_table.itemSelectionChanged.connect(self._on_selected)

        self.detail_label = QLabel("詳細: 未選択")

        self.reload_button = QPushButton("再読込")
        self.reload_button.clicked.connect(self._reload)
        self.restore_button = QPushButton("復元")
        self.restore_button.clicked.connect(self._restore_selected)
        self.hard_delete_button = QPushButton("完全削除")
        self.hard_delete_button.clicked.connect(self._hard_delete_selected)

        form = QFormLayout()
        form.addRow("対象", self.entity_selector)
        form.addRow("operator_id", self.operator_input)

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

    def _apply_role_guards(self) -> None:
        enabled = can_run_destructive_actions(self._role_context.role)
        self.restore_button.setEnabled(enabled)
        self.hard_delete_button.setEnabled(enabled)

        self.restore_button.setToolTip(
            "このロールでは実行できません" if not enabled else "削除済みデータを選択してください"
        )
        self.hard_delete_button.setToolTip(
            "このロールでは実行できません" if not enabled else "削除済みデータを選択してください"
        )

    def _reload(self) -> None:
        entity = self.entity_selector.currentText()
        self._selected = None
        self.detail_label.setText("詳細: 未選択")

        try:
            if entity == "Name":
                self._names = self._query_service.list_deleted_names()
                self._fill_name_rows(self._names)
            elif entity == "Title":
                self._titles = self._query_service.list_deleted_titles()
                self._fill_title_rows(self._titles)
            elif entity == "Subtitle":
                self._subtitles = self._query_service.list_deleted_subtitles()
                self._fill_subtitle_rows(self._subtitles)
            elif entity == "Link":
                self._links = self._query_service.list_deleted_links()
                self._fill_link_rows(self._links)
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"一覧取得に失敗しました: {exc}", is_error=True)
            return

        if self.list_table.rowCount() > 0:
            self.list_table.selectRow(0)
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
            self.list_table.setItem(
                i, 1, QTableWidgetItem(f"{row.subtitle_code} {row.subtitle_name}")
            )
            self.list_table.setItem(i, 2, QTableWidgetItem(row.deleted_at or ""))

    def _fill_link_rows(self, links: list[RelatedRow]) -> None:
        self.list_table.setRowCount(len(links))
        for i, row in enumerate(links):
            self.list_table.setItem(i, 0, QTableWidgetItem(str(row.link_id)))
            display_text = (
                f"name={row.name_id} / {row.title_name}:{row.subtitle_code} "
                f"({row.relation_type})"
            )
            self.list_table.setItem(i, 1, QTableWidgetItem(display_text))
            self.list_table.setItem(i, 2, QTableWidgetItem(row.link_deleted_at or ""))

    def _on_selected(self) -> None:
        row = self.list_table.currentRow()
        if row < 0:
            self._selected = None
            self.detail_label.setText("詳細: 未選択")
            return

        entity = self.entity_selector.currentText()
        if entity == "Name" and row < len(self._names):
            name = self._names[row]
            self._selected = _Selection(name.id, name.deleted_at)
            self.detail_label.setText(
                f"詳細: Name id={name.id} raw={name.raw_name} deleted_at={name.deleted_at}"
            )
        elif entity == "Title" and row < len(self._titles):
            title = self._titles[row]
            self._selected = _Selection(title.id, title.deleted_at)
            self.detail_label.setText(
                f"詳細: Title id={title.id} name={title.title_name} deleted_at={title.deleted_at}"
            )
        elif entity == "Subtitle" and row < len(self._subtitles):
            subtitle = self._subtitles[row]
            self._selected = _Selection(subtitle.id, subtitle.deleted_at)
            detail_text = (
                f"詳細: Subtitle id={subtitle.id} code={subtitle.subtitle_code} "
                f"deleted_at={subtitle.deleted_at}"
            )
            self.detail_label.setText(detail_text)
        elif entity == "Link" and row < len(self._links):
            link = self._links[row]
            self._selected = _Selection(link.link_id, link.link_deleted_at)
            detail_text = (
                f"詳細: Link id={link.link_id} name_id={link.name_id} "
                f"subtitle_id={link.subtitle_id} deleted_at={link.link_deleted_at}"
            )
            self.detail_label.setText(detail_text)

    def _restore_selected(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールでは復元できません", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        selected = self._require_deleted_selection()
        if selected is None:
            return

        entity = self.entity_selector.currentText()
        if not confirm_destructive_action(
            self,
            "復元の確認",
            f"{entity} ID={selected.entity_id} を復元します。よろしいですか？",
        ):
            self._set_message("復元をキャンセルしました")
            return

        try:
            if entity == "Name":
                self._core_service.restore_name(
                    selected.entity_id, operator_id, role=self._role_context.role
                )
            elif entity == "Title":
                self._core_service.restore_title(
                    selected.entity_id, operator_id, role=self._role_context.role
                )
            elif entity == "Subtitle":
                self._core_service.restore_subtitle(
                    selected.entity_id, operator_id, role=self._role_context.role
                )
            elif entity == "Link":
                self._core_service.restore_link(
                    selected.entity_id, operator_id, role=self._role_context.role
                )
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"復元に失敗しました: {exc}", is_error=True)
            return

        self._set_message("復元しました")
        self._reload()

    def _hard_delete_selected(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールでは完全削除できません", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        selected = self._require_deleted_selection()
        if selected is None:
            return

        entity = self.entity_selector.currentText()
        if not confirm_destructive_action(
            self,
            "完全削除の確認",
            f"{entity} ID={selected.entity_id} を完全削除します。この操作は元に戻せません。",
        ):
            self._set_message("完全削除をキャンセルしました")
            return

        try:
            if entity == "Name":
                self._core_service.hard_delete_name(
                    selected.entity_id, operator_id, role=self._role_context.role
                )
            elif entity == "Title":
                self._core_service.hard_delete_title(
                    selected.entity_id, operator_id, role=self._role_context.role
                )
            elif entity == "Subtitle":
                self._core_service.hard_delete_subtitle(
                    selected.entity_id, operator_id, role=self._role_context.role
                )
            elif entity == "Link":
                self._core_service.hard_delete_link(
                    selected.entity_id, operator_id, role=self._role_context.role
                )
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"完全削除に失敗しました: {exc}", is_error=True)
            return

        self._set_message("完全削除しました")
        self._reload()

    def _require_operator_id(self) -> str | None:
        operator_id = self.operator_input.text().strip()
        if not operator_id:
            self._set_message("operator_id を入力してください", is_error=True)
            return None
        return operator_id

    def _require_deleted_selection(self) -> _Selection | None:
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

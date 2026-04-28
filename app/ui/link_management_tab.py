"""Name ↔ Subtitle link management tab UI."""

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
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.application.read_models import NameSearchRow, RelatedRow, SubtitleDetail, TitleDetail
from app.ui.dialogs import confirm_destructive_action
from app.ui.permissions import can_link, can_unlink
from app.ui.relation_types import RELATION_TYPE_OPTIONS
from app.ui.role_context import RoleContext, UserRole


class LinkWriteService(Protocol):
    def link_name_to_subtitle(
        self,
        name_id: int,
        subtitle_id: int,
        relation_type: str,
        operator_id: str,
        role: UserRole = "admin",
    ) -> int: ...

    def unlink_name_from_subtitle(
        self, link_id: int, operator_id: str, role: UserRole = "admin"
    ) -> None: ...


class LinkReadService(Protocol):
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

    def list_titles(
        self, role: UserRole = "admin", *, include_deleted: bool = False
    ) -> list[TitleDetail]: ...

    def list_subtitles(
        self,
        title_id: int,
        role: UserRole = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[SubtitleDetail]: ...

    def list_related_rows(
        self,
        name_id: int,
        role: UserRole = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[RelatedRow]: ...


@dataclass(frozen=True)
class _Selection:
    id: int


class LinkManagementTab(QWidget):
    """UI for managing links between names and subtitles."""

    def __init__(
        self,
        core_service: LinkWriteService,
        query_service: LinkReadService,
        role_context: RoleContext | None = None,
    ) -> None:
        super().__init__()
        self._core_service = core_service
        self._query_service = query_service
        self._role_context = role_context or RoleContext.admin()

        self._names: list[NameSearchRow] = []
        self._titles: list[TitleDetail] = []
        self._subtitles: list[SubtitleDetail] = []
        self._links: list[RelatedRow] = []

        self._selected_name: _Selection | None = None
        self._selected_title: _Selection | None = None
        self._selected_subtitle: _Selection | None = None
        self._selected_link: _Selection | None = None

        self.operator_input = QLineEdit()
        self.operator_input.setPlaceholderText("操作者ID")
        self.operator_input.setToolTip("operator_id が必要です")

        self.relation_type_combo = QComboBox()
        self.relation_type_combo.addItem("-- relation_type を選択 --", "")
        for option in RELATION_TYPE_OPTIONS:
            self.relation_type_combo.addItem(option.label, option.value)
        self.relation_type_combo.currentIndexChanged.connect(self._on_relation_type_changed)
        self.relation_type_combo.setToolTip("relation_type を選択してください")

        self.custom_relation_type_input = QLineEdit()
        self.custom_relation_type_input.setPlaceholderText("カスタム relation_type")
        self.custom_relation_type_input.setEnabled(False)
        self.custom_relation_type_input.setToolTip(
            "other 選択時に custom relation_type を入力してください"
        )

        self.message_label = QLabel("")

        self.names_table = QTableWidget(0, 2)
        self.names_table.setHorizontalHeaderLabels(["ID", "名前"])
        self.names_table.itemSelectionChanged.connect(self._on_name_selected)

        self.titles_table = QTableWidget(0, 2)
        self.titles_table.setHorizontalHeaderLabels(["ID", "タイトル"])
        self.titles_table.itemSelectionChanged.connect(self._on_title_selected)

        self.subtitles_table = QTableWidget(0, 3)
        self.subtitles_table.setHorizontalHeaderLabels(["ID", "コード", "サブタイトル"])
        self.subtitles_table.itemSelectionChanged.connect(self._on_subtitle_selected)

        self.links_table = QTableWidget(0, 4)
        self.links_table.setHorizontalHeaderLabels(
            ["リンクID", "タイトル", "コード", "relation_type"]
        )
        self.links_table.itemSelectionChanged.connect(self._on_link_selected)

        self.refresh_button = QPushButton("再読込")
        self.refresh_button.clicked.connect(self._refresh_all)
        self.link_button = QPushButton("リンク作成")
        self.link_button.clicked.connect(self._create_link)
        self.unlink_button = QPushButton("リンク解除")
        self.unlink_button.clicked.connect(self._unlink_link)

        top_form = QFormLayout()
        top_form.addRow("操作者ID", self.operator_input)
        top_form.addRow("relation_type", self.relation_type_combo)
        top_form.addRow("custom_relation_type", self.custom_relation_type_input)

        actions = QHBoxLayout()
        actions.addWidget(self.refresh_button)
        actions.addWidget(self.link_button)
        actions.addWidget(self.unlink_button)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("名前"))
        left_layout.addWidget(self.names_table)

        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)
        middle_layout.addWidget(QLabel("タイトル"))
        middle_layout.addWidget(self.titles_table)
        middle_layout.addWidget(QLabel("サブタイトル"))
        middle_layout.addWidget(self.subtitles_table)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(QLabel("既存リンク"))
        right_layout.addWidget(self.links_table)

        splitter = QSplitter()
        splitter.addWidget(left_panel)
        splitter.addWidget(middle_panel)
        splitter.addWidget(right_panel)

        root = QVBoxLayout(self)
        root.addLayout(top_form)
        root.addLayout(actions)
        root.addWidget(self.message_label)
        root.addWidget(splitter)

        self._apply_role_guards()
        self._refresh_all()

    def _apply_role_guards(self) -> None:
        role = self._role_context.role
        link_enabled = can_link(role)
        unlink_enabled = can_unlink(role)
        self.link_button.setEnabled(link_enabled)
        self.unlink_button.setEnabled(unlink_enabled)

        self.link_button.setToolTip(
            "このロールでは実行できません"
            if not link_enabled
            else "operator_id・relation_type・Name/Subtitle選択が必要です"
        )
        self.unlink_button.setToolTip(
            "このロールでは実行できません"
            if not unlink_enabled
            else "解除対象リンクを選択してください"
        )

    def _refresh_all(self) -> None:
        try:
            self._names = self._query_service.search_names(
                include_deleted=False, role=self._role_context.role
            )
            self._titles = self._query_service.list_titles(
                include_deleted=False, role=self._role_context.role
            )
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"初期読込に失敗しました: {exc}", is_error=True)
            return

        self.names_table.setRowCount(len(self._names))
        for i, name_row in enumerate(self._names):
            self.names_table.setItem(i, 0, QTableWidgetItem(str(name_row.id)))
            self.names_table.setItem(i, 1, QTableWidgetItem(name_row.raw_name))

        self.titles_table.setRowCount(len(self._titles))
        for i, title_row in enumerate(self._titles):
            self.titles_table.setItem(i, 0, QTableWidgetItem(str(title_row.id)))
            self.titles_table.setItem(i, 1, QTableWidgetItem(title_row.title_name))

        self._selected_name = None
        self._selected_title = None
        self._selected_subtitle = None
        self._selected_link = None
        self.subtitles_table.setRowCount(0)
        self.links_table.setRowCount(0)

        if self._names:
            self.names_table.selectRow(0)
        if self._titles:
            self.titles_table.selectRow(0)

    def _on_name_selected(self) -> None:
        idx = self.names_table.currentRow()
        if idx < 0 or idx >= len(self._names):
            self._selected_name = None
            self.links_table.setRowCount(0)
            return

        self._selected_name = _Selection(id=self._names[idx].id)
        self._refresh_links()

    def _on_title_selected(self) -> None:
        idx = self.titles_table.currentRow()
        if idx < 0 or idx >= len(self._titles):
            self._selected_title = None
            self.subtitles_table.setRowCount(0)
            return

        selected = self._titles[idx]
        self._selected_title = _Selection(id=selected.id)
        self._refresh_subtitles(selected.id)

    def _on_subtitle_selected(self) -> None:
        idx = self.subtitles_table.currentRow()
        if idx < 0 or idx >= len(self._subtitles):
            self._selected_subtitle = None
            return

        self._selected_subtitle = _Selection(id=self._subtitles[idx].id)

    def _on_link_selected(self) -> None:
        idx = self.links_table.currentRow()
        if idx < 0 or idx >= len(self._links):
            self._selected_link = None
            return
        self._selected_link = _Selection(id=self._links[idx].link_id)

    def _on_relation_type_changed(self) -> None:
        selected_value = str(self.relation_type_combo.currentData())
        is_custom = selected_value == "other"
        self.custom_relation_type_input.setEnabled(is_custom)
        self.custom_relation_type_input.setToolTip(
            "custom relation_type を入力してください"
            if is_custom
            else "other 選択時のみ入力できます"
        )
        if not is_custom:
            self.custom_relation_type_input.clear()

    def _refresh_subtitles(self, title_id: int) -> None:
        try:
            self._subtitles = self._query_service.list_subtitles(
                title_id, include_deleted=False, role=self._role_context.role
            )
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"サブタイトル取得に失敗しました: {exc}", is_error=True)
            return

        self.subtitles_table.setRowCount(len(self._subtitles))
        for i, row in enumerate(self._subtitles):
            self.subtitles_table.setItem(i, 0, QTableWidgetItem(str(row.id)))
            self.subtitles_table.setItem(i, 1, QTableWidgetItem(row.subtitle_code))
            self.subtitles_table.setItem(i, 2, QTableWidgetItem(row.subtitle_name))

        self._selected_subtitle = None
        if self._subtitles:
            self.subtitles_table.selectRow(0)

    def _refresh_links(self) -> None:
        if self._selected_name is None:
            self.links_table.setRowCount(0)
            return

        try:
            self._links = self._query_service.list_related_rows(
                self._selected_name.id, include_deleted=False, role=self._role_context.role
            )
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"リンク取得に失敗しました: {exc}", is_error=True)
            return

        self.links_table.setRowCount(len(self._links))
        for i, row in enumerate(self._links):
            self.links_table.setItem(i, 0, QTableWidgetItem(str(row.link_id)))
            self.links_table.setItem(i, 1, QTableWidgetItem(row.title_name))
            self.links_table.setItem(i, 2, QTableWidgetItem(row.subtitle_code))
            self.links_table.setItem(i, 3, QTableWidgetItem(row.relation_type))

        self._selected_link = None
        if self._links:
            self.links_table.selectRow(0)

    def _create_link(self) -> None:
        if not can_link(self._role_context.role):
            self._set_message("このロールではリンク作成できません", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        relation_type = self._selected_relation_type()
        if relation_type is None:
            return

        if self._selected_name is None or self._selected_subtitle is None:
            self._set_message("Name と Subtitle を選択してください", is_error=True)
            return

        try:
            self._core_service.link_name_to_subtitle(
                self._selected_name.id,
                self._selected_subtitle.id,
                relation_type=relation_type,
                operator_id=operator_id,
                role=self._role_context.role,
            )
            self._set_message("リンク作成しました")
            self._refresh_links()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"リンク作成に失敗しました: {exc}", is_error=True)

    def _unlink_link(self) -> None:
        if not can_unlink(self._role_context.role):
            self._set_message("このロールではリンク解除できません", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        if self._selected_link is None:
            self._set_message("解除するリンクを選択してください", is_error=True)
            return

        if not confirm_destructive_action(
            self,
            "リンク解除の確認",
            f"リンクID={self._selected_link.id} を解除します。よろしいですか？",
        ):
            self._set_message("リンク解除をキャンセルしました")
            return

        try:
            self._core_service.unlink_name_from_subtitle(
                self._selected_link.id,
                operator_id=operator_id,
                role=self._role_context.role,
            )
            self._set_message("リンク解除しました")
            self._refresh_links()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"リンク解除に失敗しました: {exc}", is_error=True)

    def _selected_relation_type(self) -> str | None:
        selected_value = str(self.relation_type_combo.currentData())
        if not selected_value:
            self._set_message("relation_type を選択してください", is_error=True)
            return None

        if selected_value == "other":
            custom_value = self.custom_relation_type_input.text().strip()
            if not custom_value:
                self._set_message("custom relation_type を入力してください", is_error=True)
                return None
            return custom_value

        return selected_value

    def _require_operator_id(self) -> str | None:
        operator_id = self.operator_input.text().strip()
        if not operator_id:
            self._set_message("operator_id を入力してください", is_error=True)
            return None
        return operator_id

    def _set_message(self, message: str, *, is_error: bool = False) -> None:
        color = "#b00020" if is_error else "#0b6b0b"
        self.message_label.setStyleSheet(f"color: {color};")
        self.message_label.setText(message)

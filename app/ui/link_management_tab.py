"""Name ↔ Subtitle link management tab UI."""

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
    QVBoxLayout,
    QWidget,
)

from app.application.read_models import NameSearchRow, RelatedRow, SubtitleDetail, TitleDetail
from app.ui.dialogs import confirm_destructive_action


class LinkWriteService(Protocol):
    def link_name_to_subtitle(
        self, name_id: int, subtitle_id: int, relation_type: str, operator_id: str
    ) -> int: ...

    def unlink_name_from_subtitle(self, link_id: int, operator_id: str) -> None: ...


class LinkReadService(Protocol):
    def search_names(
        self,
        query: str | None = None,
        *,
        exact_match: bool = False,
        title_id: int | None = None,
        has_links: bool | None = None,
        include_deleted: bool = False,
    ) -> list[NameSearchRow]: ...

    def list_titles(self, *, include_deleted: bool = False) -> list[TitleDetail]: ...

    def list_subtitles(
        self, title_id: int, *, include_deleted: bool = False
    ) -> list[SubtitleDetail]: ...

    def list_related_rows(
        self, name_id: int, *, include_deleted: bool = False
    ) -> list[RelatedRow]: ...


@dataclass(frozen=True)
class _Selection:
    id: int


class LinkManagementTab(QWidget):
    """UI for managing links between names and subtitles."""

    def __init__(self, core_service: LinkWriteService, query_service: LinkReadService) -> None:
        super().__init__()
        self._core_service = core_service
        self._query_service = query_service

        self._names: list[NameSearchRow] = []
        self._titles: list[TitleDetail] = []
        self._subtitles: list[SubtitleDetail] = []
        self._links: list[RelatedRow] = []

        self._selected_name: _Selection | None = None
        self._selected_title: _Selection | None = None
        self._selected_subtitle: _Selection | None = None
        self._selected_link: _Selection | None = None

        self.operator_input = QLineEdit()
        self.operator_input.setPlaceholderText("operator_id")

        self.relation_type_input = QLineEdit()
        self.relation_type_input.setPlaceholderText("relation_type")

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
        top_form.addRow("operator_id", self.operator_input)
        top_form.addRow("relation_type", self.relation_type_input)

        actions = QHBoxLayout()
        actions.addWidget(self.refresh_button)
        actions.addWidget(self.link_button)
        actions.addWidget(self.unlink_button)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("Name"))
        left_layout.addWidget(self.names_table)

        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)
        middle_layout.addWidget(QLabel("Title"))
        middle_layout.addWidget(self.titles_table)
        middle_layout.addWidget(QLabel("Subtitle"))
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

        self._refresh_all()

    def _refresh_all(self) -> None:
        try:
            self._names = self._query_service.search_names(include_deleted=False)
            self._titles = self._query_service.list_titles(include_deleted=False)
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

    def _refresh_subtitles(self, title_id: int) -> None:
        try:
            self._subtitles = self._query_service.list_subtitles(title_id, include_deleted=False)
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
                self._selected_name.id, include_deleted=False
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
        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        relation_type = self.relation_type_input.text().strip()
        if not relation_type:
            self._set_message("relation_type を入力してください", is_error=True)
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
            )
            self._set_message("リンク作成しました")
            self._refresh_links()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"リンク作成に失敗しました: {exc}", is_error=True)

    def _unlink_link(self) -> None:
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
                self._selected_link.id, operator_id=operator_id
            )
            self._set_message("リンク解除しました")
            self._refresh_links()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"リンク解除に失敗しました: {exc}", is_error=True)

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

"""Read-only search tab implementation."""

from __future__ import annotations

from typing import Protocol

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
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

from app.application.read_models import NameDetail, NameSearchRow, RelatedRow


class SearchQueryService(Protocol):
    def search_names(
        self,
        query: str | None = None,
        *,
        exact_match: bool = False,
        title_id: int | None = None,
        has_links: bool | None = None,
        include_deleted: bool = False,
    ) -> list[NameSearchRow]: ...

    def get_name_detail(self, name_id: int) -> NameDetail: ...

    def list_related_rows(
        self, name_id: int, *, include_deleted: bool = False
    ) -> list[RelatedRow]: ...


class SearchTab(QWidget):
    """UI for search/read-only query operations."""

    def __init__(self, query_service: SearchQueryService) -> None:
        super().__init__()
        self._query_service = query_service
        self._search_rows: list[NameSearchRow] = []

        self.query_input = QLineEdit()
        self.match_mode = QComboBox()
        self.match_mode.addItems(["部分一致", "完全一致"])

        self.title_filter_input = QLineEdit()
        self.title_filter_input.setPlaceholderText("例: 1")

        self.has_links_filter = QComboBox()
        self.has_links_filter.addItems(["指定なし", "あり", "なし"])

        self.include_deleted_checkbox = QCheckBox("削除済みを含む")

        self.search_button = QPushButton("検索")
        self.search_button.clicked.connect(self._on_search_clicked)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #b00020;")

        self.results_table = QTableWidget(0, 4)
        self.results_table.setHorizontalHeaderLabels(["ID", "名前", "紐づき数", "削除状態"])
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.itemSelectionChanged.connect(self._on_selection_changed)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)

        self.related_table = QTableWidget(0, 4)
        self.related_table.setHorizontalHeaderLabels(
            ["リンクID", "タイトル", "コード", "サブタイトル"]
        )
        self.related_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        filter_form = QFormLayout()
        filter_form.addRow("検索語", self.query_input)
        filter_form.addRow("一致条件", self.match_mode)
        filter_form.addRow("タイトルID", self.title_filter_input)
        filter_form.addRow("紐づき", self.has_links_filter)

        top_controls = QHBoxLayout()
        top_controls.addWidget(self.include_deleted_checkbox)
        top_controls.addStretch(1)
        top_controls.addWidget(self.search_button)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addLayout(filter_form)
        left_layout.addLayout(top_controls)
        left_layout.addWidget(self.error_label)
        left_layout.addWidget(self.results_table)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(QLabel("詳細"))
        right_layout.addWidget(self.detail_text)
        right_layout.addWidget(QLabel("関連行"))
        right_layout.addWidget(self.related_table)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        root_layout = QVBoxLayout(self)
        root_layout.addWidget(splitter)

        self._on_search_clicked()

    def _on_search_clicked(self) -> None:
        self.error_label.setText("")
        try:
            title_id = self._parse_optional_int(self.title_filter_input.text())
            has_links = self._parse_has_links()
            rows = self._query_service.search_names(
                query=self.query_input.text(),
                exact_match=self.match_mode.currentText() == "完全一致",
                title_id=title_id,
                has_links=has_links,
                include_deleted=self.include_deleted_checkbox.isChecked(),
            )
        except Exception as exc:  # noqa: BLE001
            self._search_rows = []
            self.results_table.setRowCount(0)
            self.detail_text.clear()
            self.related_table.setRowCount(0)
            self.error_label.setText(f"検索に失敗しました: {exc}")
            return

        self._search_rows = rows
        self._render_results(rows)

    def _on_selection_changed(self) -> None:
        index = self.results_table.currentRow()
        if index < 0 or index >= len(self._search_rows):
            self.detail_text.clear()
            self.related_table.setRowCount(0)
            return

        selected = self._search_rows[index]
        try:
            detail = self._query_service.get_name_detail(selected.id)
            related_rows = self._query_service.list_related_rows(
                selected.id,
                include_deleted=self.include_deleted_checkbox.isChecked(),
            )
        except Exception as exc:  # noqa: BLE001
            self.error_label.setText(f"詳細取得に失敗しました: {exc}")
            return

        self._render_detail(detail)
        self._render_related(related_rows)

    def _render_results(self, rows: list[NameSearchRow]) -> None:
        self.results_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.results_table.setItem(i, 0, QTableWidgetItem(str(row.id)))
            self.results_table.setItem(i, 1, QTableWidgetItem(row.raw_name))
            self.results_table.setItem(i, 2, QTableWidgetItem(str(row.linked_count)))
            status = "削除済み" if row.deleted_at else "有効"
            self.results_table.setItem(i, 3, QTableWidgetItem(status))

        if rows:
            self.results_table.selectRow(0)
        else:
            self.detail_text.clear()
            self.related_table.setRowCount(0)

    def _render_detail(self, detail: NameDetail) -> None:
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

    def _render_related(self, rows: list[RelatedRow]) -> None:
        self.related_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.related_table.setItem(i, 0, QTableWidgetItem(str(row.link_id)))
            self.related_table.setItem(i, 1, QTableWidgetItem(row.title_name))
            self.related_table.setItem(i, 2, QTableWidgetItem(row.subtitle_code))
            self.related_table.setItem(i, 3, QTableWidgetItem(row.subtitle_name))

    def _parse_optional_int(self, value: str) -> int | None:
        stripped = value.strip()
        if not stripped:
            return None
        return int(stripped)

    def _parse_has_links(self) -> bool | None:
        text = self.has_links_filter.currentText()
        if text == "あり":
            return True
        if text == "なし":
            return False
        return None

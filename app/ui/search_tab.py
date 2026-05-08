"""Read-only search tab implementation."""

from __future__ import annotations

from typing import Protocol

from PySide6.QtWidgets import (
    QCheckBox,
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

from app.application.read_models import NameDetail, NameSearchRow, RelatedRow
from app.ui.role_context import RoleContext, UserRole
from app.ui.ui_style import PageHeader, compact_layout


class SearchQueryService(Protocol):
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

    def list_related_rows(
        self,
        name_id: int,
        role: UserRole = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[RelatedRow]: ...


class SearchTab(QWidget):
    """UI for search/read-only query operations."""

    def __init__(
        self, query_service: SearchQueryService, role_context: RoleContext | None = None
    ) -> None:
        super().__init__()
        self._query_service = query_service
        self._role_context = role_context or RoleContext.admin()
        self._search_rows: list[NameSearchRow] = []
        self._details_by_id: dict[int, NameDetail] = {}

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("名前で検索（例: 山田、Alice）")
        self.query_input.returnPressed.connect(self._on_search_clicked)
        self.match_mode = QComboBox()
        self.match_mode.addItems(["部分一致", "完全一致"])
        self.has_links_filter = QComboBox()
        self.has_links_filter.addItems(["すべて", "関連あり", "関連なし"])
        self.include_deleted_checkbox = QCheckBox("削除済みも含める")

        self.search_button = QPushButton("検索")
        self.search_button.clicked.connect(self._on_search_clicked)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ff8a8a;")

        self.results_table = QTableWidget(0, 7)
        self.results_table.setHorizontalHeaderLabels(
            ["内部ID", "名前", "検索用表記", "関連数", "状態", "更新日時", "備考"]
        )
        self.results_table.setColumnHidden(0, True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.itemSelectionChanged.connect(self._on_selection_changed)

        self.related_table = QTableWidget(0, 4)
        self.related_table.setHorizontalHeaderLabels(
            ["内部リンクID", "タイトル", "管理番号", "サブタイトル"]
        )
        self.related_table.setColumnHidden(0, True)
        self.related_table.setColumnHidden(2, True)
        self.related_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        filter_form = QFormLayout()
        compact_layout(filter_form, margins=2, spacing=3)
        filter_form.addRow("検索語", self.query_input)
        filter_form.addRow("一致条件", self.match_mode)
        filter_form.addRow("関連", self.has_links_filter)

        top_controls = QHBoxLayout()
        compact_layout(top_controls, margins=0, spacing=4)
        top_controls.addWidget(self.include_deleted_checkbox)
        top_controls.addStretch(1)
        top_controls.addWidget(self.search_button)

        root_layout = QVBoxLayout(self)
        compact_layout(root_layout, margins=5, spacing=4)
        root_layout.addWidget(PageHeader("検索", "名前・検索用表記・状態・備考を一覧で確認します。"))
        root_layout.addLayout(filter_form)
        root_layout.addLayout(top_controls)
        root_layout.addWidget(self.error_label)
        root_layout.addWidget(QLabel("検索結果（詳細統合）"))
        root_layout.addWidget(self.results_table, 3)
        root_layout.addWidget(QLabel("関連タイトル・サブタイトル"))
        root_layout.addWidget(self.related_table, 2)

        self._on_search_clicked()

    def _on_search_clicked(self) -> None:
        self.error_label.setText("")
        try:
            has_links = self._parse_has_links()
            rows = self._query_service.search_names(
                query=self.query_input.text(),
                role=self._role_context.role,
                exact_match=self.match_mode.currentText() == "完全一致",
                title_id=None,
                has_links=has_links,
                include_deleted=self.include_deleted_checkbox.isChecked(),
            )
        except Exception as exc:  # noqa: BLE001
            self._search_rows = []
            self._details_by_id = {}
            self.results_table.setRowCount(0)
            self.related_table.setRowCount(0)
            self.error_label.setText(f"検索に失敗しました: {exc}")
            return

        self._search_rows = rows
        self._details_by_id = {}
        self._render_results(rows)

    def _on_selection_changed(self) -> None:
        index = self.results_table.currentRow()
        if index < 0 or index >= len(self._search_rows):
            self.related_table.setRowCount(0)
            return

        selected = self._search_rows[index]
        try:
            related_rows = self._query_service.list_related_rows(
                selected.id,
                role=self._role_context.role,
                include_deleted=self.include_deleted_checkbox.isChecked(),
            )
        except Exception as exc:  # noqa: BLE001
            self.error_label.setText(f"関連取得に失敗しました: {exc}")
            return

        self._render_related(related_rows)

    def _render_results(self, rows: list[NameSearchRow]) -> None:
        self.results_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            detail = self._get_detail(row.id)
            self.results_table.setItem(i, 0, QTableWidgetItem(str(row.id)))
            self.results_table.setItem(i, 1, QTableWidgetItem(row.raw_name))
            self.results_table.setItem(i, 2, QTableWidgetItem(row.normalized_name))
            self.results_table.setItem(i, 3, QTableWidgetItem(str(row.linked_count)))
            status = "削除済み" if row.deleted_at else "使用中"
            self.results_table.setItem(i, 4, QTableWidgetItem(status))
            self.results_table.setItem(i, 5, QTableWidgetItem(detail.updated_at if detail else ""))
            self.results_table.setItem(i, 6, QTableWidgetItem(detail.note if detail and detail.note else ""))

        if rows:
            self.results_table.selectRow(0)
        else:
            self.related_table.setRowCount(0)

    def _get_detail(self, name_id: int) -> NameDetail | None:
        if name_id in self._details_by_id:
            return self._details_by_id[name_id]
        try:
            detail = self._query_service.get_name_detail(name_id, role=self._role_context.role)
        except Exception as exc:  # noqa: BLE001
            self.error_label.setText(f"詳細取得に失敗しました: {exc}")
            return None
        self._details_by_id[name_id] = detail
        return detail

    def _render_related(self, rows: list[RelatedRow]) -> None:
        self.related_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.related_table.setItem(i, 0, QTableWidgetItem(str(row.link_id)))
            self.related_table.setItem(i, 1, QTableWidgetItem(row.title_name))
            self.related_table.setItem(i, 2, QTableWidgetItem(row.subtitle_code))
            self.related_table.setItem(i, 3, QTableWidgetItem(row.subtitle_name))

    def _parse_has_links(self) -> bool | None:
        text = self.has_links_filter.currentText()
        if text == "関連あり":
            return True
        if text == "関連なし":
            return False
        return None

"""Rich search tab wrapper for phase 1 admin UI polish."""

from __future__ import annotations

from typing import Any

from app.ui.search_tab import SearchTab as BaseSearchTab
from PySide6.QtWidgets import QLabel, QVBoxLayout


class SearchTab(BaseSearchTab):
    """Add summary and selection context to the existing search tab."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._rich_search_ready = False
        self.summary_label = QLabel("")
        self.selection_summary_label = QLabel("")
        super().__init__(*args, **kwargs)
        self.summary_label.setObjectName("SearchSummaryBar")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet(
            "QLabel { color: #a5f3fc; background: #17394a; "
            "border: 1px solid #22d3ee; border-radius: 6px; "
            "padding: 5px 7px; font-weight: 700; }"
        )
        self.selection_summary_label.setObjectName("SearchSelectionSummary")
        self.selection_summary_label.setWordWrap(True)
        self.selection_summary_label.setStyleSheet(
            "QLabel { color: #ddd6fe; background: #2e245c; "
            "border: 1px solid #a78bfa; border-radius: 6px; "
            "padding: 5px 7px; font-weight: 700; }"
        )
        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            layout.insertWidget(1, self.summary_label)
            layout.insertWidget(
                max(layout.count() - 1, 1),
                self.selection_summary_label,
            )
        self._rich_search_ready = True
        self._update_rich_search_summaries()

    def _on_search_clicked(self) -> None:
        super()._on_search_clicked()
        if self._rich_search_ready:
            self._update_rich_search_summaries()

    def _on_selection_changed(self) -> None:
        super()._on_selection_changed()
        if self._rich_search_ready:
            self._update_rich_search_summaries()

    def _selected_row_indexes(self) -> list[int]:
        selection_model = self.results_table.selectionModel()
        if selection_model is None:
            current = self.results_table.currentRow()
            return [current] if 0 <= current < len(self._search_rows) else []
        rows = sorted({index.row() for index in selection_model.selectedRows()})
        return [row for row in rows if 0 <= row < len(self._search_rows)]

    def _summary_row_index(self, selected_rows: list[int]) -> int | None:
        current = self.results_table.currentRow()
        if 0 <= current < len(self._search_rows):
            return current
        if selected_rows:
            return selected_rows[0]
        return None

    def _related_total_for_row(self, row_index: int | None) -> int:
        if row_index is None:
            return 0
        selected = self._search_rows[row_index]
        return selected.title_related_count + selected.subtitle_related_count

    def _update_rich_search_summaries(self) -> None:
        total = len(self._search_rows)
        deleted = sum(1 for row in self._search_rows if row.deleted_at)
        selected_rows = self._selected_row_indexes()
        selected_count = len(selected_rows)
        summary_row_index = self._summary_row_index(selected_rows)
        related_total = self._related_total_for_row(summary_row_index)
        include_deleted = "ON" if self.include_deleted_checkbox.isChecked() else "OFF"
        self.summary_label.setText(
            f"検索結果 {total}件 / 表示中 {total}件 / 選択中 {selected_count}件 / "
            f"関連 {related_total}件 / 有効 {total - deleted}件 / "
            f"削除済み {deleted}件 / 削除済み含む {include_deleted}"
        )
        if summary_row_index is None:
            self.selection_summary_label.setText(
                "選択中の名前: 未選択 / 公開ID: - / 関連合計 0件"
            )
            return
        selected = self._search_rows[summary_row_index]
        public_id = selected.public_id or "未採番"
        self.selection_summary_label.setText(
            f"選択中の名前: {selected.raw_name} / 公開ID: {public_id} / "
            f"タイトル関連 {selected.title_related_count}件 / "
            f"サブタイトル関連 {selected.subtitle_related_count}件 / "
            f"関連合計 {related_total}件"
        )

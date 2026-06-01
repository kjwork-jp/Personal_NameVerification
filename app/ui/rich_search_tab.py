"""Rich search tab wrapper for phase 1 admin UI polish."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout

from app.ui.search_tab import SearchTab as BaseSearchTab


class SearchTab(BaseSearchTab):
    """Add summary and selection context to the existing search tab."""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self.summary_label = QLabel("")
        self.summary_label.setObjectName("SearchSummaryBar")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet(
            "QLabel { color: #a5f3fc; background: #17394a; "
            "border: 1px solid #22d3ee; border-radius: 6px; "
            "padding: 5px 7px; font-weight: 700; }"
        )
        self.selection_summary_label = QLabel("")
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
            layout.insertWidget(max(layout.count() - 1, 1), self.selection_summary_label)
        self._update_rich_search_summaries()

    def _on_search_clicked(self) -> None:
        super()._on_search_clicked()
        if hasattr(self, "summary_label"):
            self._update_rich_search_summaries()

    def _on_selection_changed(self) -> None:
        super()._on_selection_changed()
        if hasattr(self, "summary_label"):
            self._update_rich_search_summaries()

    def _update_rich_search_summaries(self) -> None:
        total = len(self._search_rows)
        deleted = sum(1 for row in self._search_rows if row.deleted_at)
        selected_index = self.results_table.currentRow()
        selected_count = 1 if 0 <= selected_index < total else 0
        related_count = self.related_table.rowCount()
        include_deleted = "ON" if self.include_deleted_checkbox.isChecked() else "OFF"
        self.summary_label.setText(
            f"検索結果 {total}件 / 表示中 {total}件 / 選択中 {selected_count}件 / "
            f"関連 {related_count}件 / 有効 {total - deleted}件 / "
            f"削除済み {deleted}件 / 削除済み含む {include_deleted}"
        )
        if selected_count == 0:
            self.selection_summary_label.setText(
                "選択中の名前: 未選択 / 公開ID: - / 関連合計 0件"
            )
            return
        selected = self._search_rows[selected_index]
        self.selection_summary_label.setText(
            f"選択中の名前: {selected.raw_name} / 公開ID: {selected.public_id or '未採番'} / "
            f"タイトル関連 {selected.title_related_count}件 / "
            f"サブタイトル関連 {selected.subtitle_related_count}件 / "
            f"関連合計 {related_count}件"
        )

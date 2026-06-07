"""Summary counter extension for the base title/subtitle management tab."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from app.ui.ui_style import apply_workflow_accent

_PATCHED_ATTR = "_title_subtitle_summary_counters_installed"
_LINKED_NAMES_COLUMN = 6
_EMPTY_LINKED_NAMES = {"", "なし", "-"}


def install_title_subtitle_summary_counters() -> None:
    """Install list summary counters on TitleSubtitleManagementTab once."""
    from app.ui.title_subtitle_management_tab import TitleSubtitleManagementTab

    target: Any = TitleSubtitleManagementTab
    if getattr(target, _PATCHED_ATTR, False):
        _install_duplicate_prechecks()
        return

    original_init = target.__init__
    original_refresh_titles = target._refresh_titles
    original_refresh_subtitles = target._refresh_subtitles
    original_select_title = target._select_title
    original_clear_selection = target._clear_selection
    original_select_subtitle = target._select_subtitle
    original_update_action_states = target._update_action_states

    def init_with_summary(self: Any, *args: Any, **kwargs: Any) -> None:
        original_init(self, *args, **kwargs)
        _ensure_summary_label(self)
        _update_summary_label(self)

    def refresh_titles_with_summary(
        self: Any,
        selected_title_id: int | None = None,
    ) -> None:
        original_refresh_titles(self, selected_title_id)
        _update_summary_label(self)

    def refresh_subtitles_with_summary(
        self: Any,
        selected_subtitle_id: int | None = None,
    ) -> None:
        original_refresh_subtitles(self, selected_subtitle_id)
        _update_summary_label(self)

    def select_title_with_summary(self: Any, row: Any) -> None:
        original_select_title(self, row)
        _update_summary_label(self)

    def clear_selection_with_summary(self: Any) -> None:
        original_clear_selection(self)
        _update_summary_label(self)

    def select_subtitle_with_summary(self: Any, row: Any) -> None:
        original_select_subtitle(self, row)
        _update_summary_label(self)

    def update_action_states_with_summary(self: Any) -> None:
        original_update_action_states(self)
        _update_summary_label(self)

    target.__init__ = init_with_summary
    target._refresh_titles = refresh_titles_with_summary
    target._refresh_subtitles = refresh_subtitles_with_summary
    target._select_title = select_title_with_summary
    target._clear_selection = clear_selection_with_summary
    target._select_subtitle = select_subtitle_with_summary
    target._update_action_states = update_action_states_with_summary
    setattr(target, _PATCHED_ATTR, True)
    _install_duplicate_prechecks()


def _install_duplicate_prechecks() -> None:
    from app.ui.title_subtitle_duplicate_precheck import install_title_subtitle_duplicate_precheck
    from app.ui.title_subtitle_update_duplicate_precheck import (
        install_title_subtitle_update_duplicate_precheck,
    )

    install_title_subtitle_duplicate_precheck()
    install_title_subtitle_update_duplicate_precheck()


def _ensure_summary_label(tab: Any) -> None:
    if hasattr(tab, "title_subtitle_list_summary_label"):
        return
    label = QLabel(
        "タイトル一覧 0件 / 選択中タイトル 0件 / 有効タイトル 0件 / "
        "削除済みタイトル 0件 / 関連名あり 0件 / "
        "表示中サブタイトル 0件 / 選択中サブタイトル 0件 / "
        "有効サブタイトル 0件 / 削除済みサブタイトル 0件"
    )
    label.setWordWrap(True)
    label.setMinimumHeight(0)
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    label.setProperty("title_subtitle_list_summary_counter", True)
    apply_workflow_accent(label, "list")
    tab.title_subtitle_list_summary_label = label
    layout = tab.list_tab.layout()
    if layout is not None:
        layout.insertWidget(2, label)
    tab.setProperty("title_subtitle_list_summary_counters", True)


def _update_summary_label(tab: Any) -> None:
    if not hasattr(tab, "title_subtitle_list_summary_label"):
        return
    titles = getattr(tab, "_titles", [])
    subtitles = getattr(tab, "_subtitles", [])
    total_titles = len(titles)
    deleted_titles = sum(1 for row in titles if row.deleted_at)
    active_titles = total_titles - deleted_titles
    selected_title_count = 1 if getattr(tab, "_selected_title", None) is not None else 0
    selected_subtitle_count = 1 if getattr(tab, "_selected_subtitle", None) is not None else 0
    linked_titles = _linked_title_count_from_rendered_table(tab)
    total_subtitles = len(subtitles)
    deleted_subtitles = sum(1 for row in subtitles if row.deleted_at)
    active_subtitles = total_subtitles - deleted_subtitles
    tab.title_subtitle_list_summary_label.setText(
        f"タイトル一覧 {total_titles}件 / "
        f"選択中タイトル {selected_title_count}件 / "
        f"有効タイトル {active_titles}件 / "
        f"削除済みタイトル {deleted_titles}件 / "
        f"関連名あり {linked_titles}件 / "
        f"表示中サブタイトル {total_subtitles}件 / "
        f"選択中サブタイトル {selected_subtitle_count}件 / "
        f"有効サブタイトル {active_subtitles}件 / "
        f"削除済みサブタイトル {deleted_subtitles}件"
    )


def _linked_title_count_from_rendered_table(tab: Any) -> int:
    """Count linked-title rows from the already rendered title table.

    The base table already populates the linked-name column during title refresh.
    Reading that rendered value avoids issuing one list_names_for_title query per title
    during ordinary selection/action-state updates.
    """
    table = getattr(tab, "titles_table", None)
    if table is None:
        return 0
    count = 0
    for row in range(table.rowCount()):
        item = table.item(row, _LINKED_NAMES_COLUMN)
        if item is not None and item.text().strip() not in _EMPTY_LINKED_NAMES:
            count += 1
    return count

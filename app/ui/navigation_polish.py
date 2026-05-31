"""Navigation polish helpers for workflow tab guidance."""

from __future__ import annotations

from PySide6.QtWidgets import QTabWidget


_WORKFLOW_TAB_TOOLTIPS = {
    "一覧": "登録済みデータを確認します。編集前に対象を選ぶ入口です。",
    "新規追加": "選択中データを引き継がず、空フォームから新規登録します。",
    "編集": "一覧または選択欄で対象を明示してから更新します。",
    "削除": "admin向けの削除・復元・完全削除操作です。",
    "ガイド": "この画面の操作順とロール別の実行範囲を確認します。",
}


def _normalized_tab_name(label: str) -> str:
    """Normalize labels such as '1. 一覧' back to their semantic name."""

    text = label.strip()
    if ". " in text and text.split(". ", 1)[0].isdigit():
        return text.split(". ", 1)[1]
    return text


def apply_workflow_tab_navigation(tab_widget: QTabWidget) -> None:
    """Apply consistent workflow guidance without changing visible tab labels."""

    for index in range(tab_widget.count()):
        label = _normalized_tab_name(tab_widget.tabText(index))
        tooltip = _WORKFLOW_TAB_TOOLTIPS.get(label)
        if tooltip:
            tab_widget.setTabToolTip(index, tooltip)
    tab_widget.setProperty("navigation_polish_applied", True)
    tab_widget.setProperty(
        "navigation_order_hint",
        "一覧 -> 新規追加 -> 編集 -> 削除 -> ガイド",
    )

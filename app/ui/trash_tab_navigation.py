"""Navigation restructuring helpers for the Trash tab."""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QFormLayout, QTabWidget, QVBoxLayout, QWidget

_TRASH_TAB_FILTERS = [
    ("すべて", "すべて"),
    ("削除済み名前", "名前"),
    ("削除済みタイトル", "タイトル"),
    ("削除済みサブタイトル", "サブタイトル"),
    ("削除済みリンク", "リンク"),
]


def apply_trash_subtabs(widget: QWidget) -> None:
    """Add entity-oriented subtabs to the already-built TrashTab.

    The existing TrashTab keeps one shared table and one hidden entity selector.
    This helper adds visible subtabs that drive the same selector, so existing
    reload, restore, hard-delete, tests, and RBAC behavior remain unchanged.
    """

    if getattr(widget, "trash_entity_tabs", None) is not None:
        return

    root_layout = widget.layout()
    entity_selector = getattr(widget, "entity_selector", None)
    if not isinstance(root_layout, QVBoxLayout) or not isinstance(entity_selector, QComboBox):
        return

    sub_tabs = QTabWidget(widget)
    sub_tabs.setObjectName("trashEntitySubTabs")
    for title, _selector_text in _TRASH_TAB_FILTERS:
        sub_tabs.addTab(QWidget(sub_tabs), title)

    sync_guard = {"active": False}

    def _sync_selector_from_tab(index: int) -> None:
        if sync_guard["active"]:
            return
        if index < 0 or index >= len(_TRASH_TAB_FILTERS):
            return
        _title, selector_text = _TRASH_TAB_FILTERS[index]
        if entity_selector.currentText() == selector_text:
            return
        sync_guard["active"] = True
        entity_selector.setCurrentText(selector_text)
        sync_guard["active"] = False

    def _sync_tab_from_selector(text: str) -> None:
        if sync_guard["active"]:
            return
        target_index = _index_for_selector_text(text)
        if target_index is None or sub_tabs.currentIndex() == target_index:
            return
        sync_guard["active"] = True
        sub_tabs.setCurrentIndex(target_index)
        sync_guard["active"] = False

    sub_tabs.currentChanged.connect(_sync_selector_from_tab)
    entity_selector.currentTextChanged.connect(_sync_tab_from_selector)

    insert_index = 1 if root_layout.count() > 0 else 0
    root_layout.insertWidget(insert_index, sub_tabs)
    _hide_legacy_selector(root_layout, entity_selector)
    widget.trash_entity_tabs = sub_tabs
    _sync_tab_from_selector(entity_selector.currentText())


def _index_for_selector_text(text: str) -> int | None:
    normalized = {
        "All": "すべて",
        "Name": "名前",
        "Title": "タイトル",
        "Subtitle": "サブタイトル",
        "Link": "リンク",
    }.get(text, text)
    for index, (_tab_title, selector_text) in enumerate(_TRASH_TAB_FILTERS):
        if selector_text == normalized:
            return index
    return None


def _hide_legacy_selector(root_layout: QVBoxLayout, entity_selector: QComboBox) -> None:
    form_layout = _find_form_layout(root_layout)
    if form_layout is None:
        return
    label = form_layout.labelForField(entity_selector)
    if label is not None:
        label.setVisible(False)
    entity_selector.setVisible(False)


def _find_form_layout(root_layout: QVBoxLayout) -> QFormLayout | None:
    for index in range(root_layout.count()):
        item = root_layout.itemAt(index)
        if item is None:
            continue
        layout = item.layout()
        if isinstance(layout, QFormLayout):
            return layout
    return None

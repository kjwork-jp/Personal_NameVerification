"""Helpers that move CRUD screens toward list-first navigation."""

from __future__ import annotations

from PySide6.QtWidgets import QTableWidget, QVBoxLayout, QWidget


def apply_crud_list_first(widget: QWidget, tab_title: str) -> None:
    """Move entity lists before edit forms where the tab structure supports it."""

    if widget.property("has_list_first_layout") is True:
        return

    if tab_title == "名前を管理":
        _move_child_table_to_top(widget, "names_table")
    elif tab_title in {"タイトルを管理", "サブタイトルを管理"}:
        editor = getattr(widget, "editor", None)
        if isinstance(editor, QWidget):
            _move_child_table_to_top(editor, "titles_table", parent_attr="title_panel")
            _move_child_table_to_top(editor, "subtitles_table", parent_attr="subtitle_panel")

    widget.setProperty("has_list_first_layout", True)


def _move_child_table_to_top(
    owner: QWidget,
    table_attr: str,
    *,
    parent_attr: str | None = None,
) -> None:
    parent = getattr(owner, parent_attr) if parent_attr is not None else owner
    table = getattr(owner, table_attr, None)
    if not isinstance(parent, QWidget) or not isinstance(table, QTableWidget):
        return

    layout = parent.layout()
    if not isinstance(layout, QVBoxLayout):
        return

    table_index = layout.indexOf(table)
    if table_index < 0:
        return

    insert_index = _list_insert_index(layout)
    if table_index == insert_index:
        return

    item = layout.takeAt(table_index)
    if item is None:
        return
    layout.insertWidget(insert_index, table, 2)


def _list_insert_index(layout: QVBoxLayout) -> int:
    """Insert after the panel title/header area, before edit forms and actions."""

    return min(1, layout.count())

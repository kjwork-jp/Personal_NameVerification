"""Helpers that move CRUD screens toward list-first navigation."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QTableWidget, QVBoxLayout, QWidget


_LIST_FIRST_MESSAGES: dict[str, str] = {
    "名前を管理": "一覧から名前を選択し、下の入力欄で内容確認・更新・操作します。新規作成時は選択状態を気にせず入力してください。",
    "タイトル/サブタイトル管理": "一覧からタイトルまたはサブタイトルを選択し、入力欄で内容確認・更新します。復元と完全削除は削除データタブで行います。",
    "タイトルを管理": "一覧からタイトルを選択し、入力欄で内容確認・更新します。",
    "サブタイトルを管理": "一覧からタイトルとサブタイトルを選択し、入力欄で内容確認・更新します。",
    "関連付け": "登録/解除対象を上から順に選択して操作します。再読込で候補を最新化します。",
}


def apply_crud_list_first(widget: QWidget, tab_title: str) -> None:
    """Move entity lists before edit forms where the tab structure supports it."""

    if widget.property("has_list_first_layout") is True:
        return

    _insert_list_first_hint(widget, tab_title)

    if tab_title == "名前を管理":
        _move_child_table_to_top(widget, "names_table")
    elif tab_title in {"タイトル/サブタイトル管理", "タイトルを管理", "サブタイトルを管理"}:
        _apply_title_subtitle_list_first(widget)
    elif tab_title == "関連付け":
        _mark_relationship_tab(widget)

    widget.setProperty("has_list_first_layout", True)


def _apply_title_subtitle_list_first(widget: QWidget) -> None:
    title_tab = getattr(widget, "title_tab", None)
    subtitle_tab = getattr(widget, "subtitle_tab", None)
    if isinstance(title_tab, QWidget):
        _apply_title_subtitle_editor_list_first(getattr(title_tab, "editor", None))
        _insert_list_first_hint(title_tab, "タイトルを管理")
    if isinstance(subtitle_tab, QWidget):
        _apply_title_subtitle_editor_list_first(getattr(subtitle_tab, "editor", None))
        _insert_list_first_hint(subtitle_tab, "サブタイトルを管理")

    editor = getattr(widget, "editor", None)
    _apply_title_subtitle_editor_list_first(editor)


def _apply_title_subtitle_editor_list_first(editor: object) -> None:
    if not isinstance(editor, QWidget):
        return
    _move_child_table_to_top(editor, "titles_table", parent_attr="title_panel")
    _move_child_table_to_top(editor, "subtitles_table", parent_attr="subtitle_panel")


def _mark_relationship_tab(widget: QWidget) -> None:
    widget.setProperty("relationship_workflow_guided", True)


def _insert_list_first_hint(widget: QWidget, tab_title: str) -> None:
    if widget.property("has_list_first_hint") is True:
        return
    message = _LIST_FIRST_MESSAGES.get(tab_title)
    if message is None:
        return
    layout = widget.layout()
    if not isinstance(layout, QVBoxLayout):
        return
    hint = QLabel(message)
    hint.setObjectName("listFirstWorkflowHint")
    hint.setWordWrap(True)
    hint.setStyleSheet(
        "QLabel#listFirstWorkflowHint {"
        "color: #dbeafe;"
        "background-color: #1f2937;"
        "border: 1px solid #60a5fa;"
        "border-radius: 6px;"
        "padding: 4px 6px;"
        "font-weight: 600;"
        "}"
    )
    layout.insertWidget(_hint_insert_index(layout), hint)
    widget.setProperty("has_list_first_hint", True)


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


def _hint_insert_index(layout: QVBoxLayout) -> int:
    """Insert after the page header where possible."""

    return min(1, layout.count())


def _list_insert_index(layout: QVBoxLayout) -> int:
    """Insert after the panel title/header area, before edit forms and actions."""

    return min(1, layout.count())

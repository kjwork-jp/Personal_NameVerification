"""データ入出力タブのナビゲーション再構成ヘルパー。"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QLayout,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.ui.operations_guidance import (
    DATA_IO_GROUP_DESCRIPTIONS,
    DATA_IO_LOG_DESCRIPTION,
    DATA_IO_PAGE_DESCRIPTION,
    DATA_IO_PAGE_TITLE,
    DATA_IO_RESULT_DESCRIPTION,
)
from app.ui.ui_style import PageHeader, make_workflow_accent_label

_GUIDE_TEXT_BY_ROLE = {
    "viewer": """
データ入出力タブの操作ガイド（viewer）

この権限では、実行ログの参照のみ利用できます。
データ出力 / バックアップ / 復元 / データ取込は表示しません。

1. 実行ログ
   データ入出力タブの実行ログを確認・絞り込みできます。
   ログ出力は出力操作のため、viewerでは利用できません。

補足:
   viewerは参照専用です。DB更新、出力、バックアップ、復元、取込は行えません。
""".strip(),
    "editor": """
データ入出力タブの操作ガイド（editor）

この権限では、通常のデータ出力とバックアップのみ利用できます。
復元 / データ取込は破壊的操作のため表示しません。

1. データ出力
   CSV / JSON / SQLダンプを出力します。

2. バックアップ
   現在のSQLite DBをバックアップします。

3. 実行ログ
   データ入出力タブの実行ログを確認・絞り込み・出力します。

補足:
   editorは通常作業向けです。DB置換や外部データ取込はadminで実行してください。
""".strip(),
    "admin": """
データ入出力タブの操作ガイド（admin）

この権限では、データ入出力の全操作を利用できます。
復元 / データ取込は破壊的操作のため、実行前に必ずバックアップを取得してください。

1. データ出力
   CSV / JSON / SQLダンプを出力します。

2. バックアップ
   現在のSQLite DBをバックアップします。

3. 復元
   バックアップDBで対象DBを置換します。破壊的操作です。

4. データ取込
   CSV / JSONからDBへ取り込みます。破壊的操作です。

5. 実行ログ
   データ入出力タブの実行ログを確認・絞り込み・出力します。
""".strip(),
}


def apply_operations_subtabs(widget: QWidget) -> None:
    """構築済みのOperationsTabを処理別サブタブへ再構成する。"""

    if getattr(widget, "operations_subtabs", None) is not None:
        return

    root_layout = widget.layout()
    if not isinstance(root_layout, QVBoxLayout):
        return

    grid_index, operations_grid = _take_first_grid_layout(root_layout)
    if operations_grid is None:
        return

    groups = _take_group_boxes_from_grid(operations_grid)
    if not groups:
        return

    logs_group = _take_group_box_by_title(root_layout, "データ入出力 実行ログ")
    _insert_result_hint(root_layout, widget)

    sub_tabs = QTabWidget(widget)
    sub_tabs.setObjectName("operationsSubTabs")
    role = str(getattr(widget, "_role", "admin"))
    sub_tabs.addTab(_build_guide_page(role), "ガイド")

    section_order = [
        ("データ出力", "データ出力"),
        ("バックアップ", "バックアップ"),
        ("復元（破壊的操作）", "復元"),
        ("データ取込（破壊的操作）", "データ取込"),
    ]
    for group_title, tab_title in section_order:
        group = groups.get(group_title)
        if group is not None:
            sub_tabs.addTab(_page_with_group(group), tab_title)

    if logs_group is not None:
        sub_tabs.addTab(_page_with_group(logs_group), "実行ログ")

    insert_index = max(0, grid_index)
    root_layout.insertWidget(insert_index, sub_tabs, 1)
    widget.operations_subtabs = sub_tabs


def _build_guide_page(role: str) -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(8)
    header = PageHeader(DATA_IO_PAGE_TITLE, DATA_IO_PAGE_DESCRIPTION)
    header.setProperty("data_io_navigation_header", True)
    layout.addWidget(header)
    label = QLabel(_GUIDE_TEXT_BY_ROLE.get(role, _GUIDE_TEXT_BY_ROLE["admin"]))
    label.setObjectName("operationsRoleGuideLabel")
    label.setWordWrap(True)
    label.setTextInteractionFlags(label.textInteractionFlags())
    layout.addWidget(label)
    layout.addStretch(1)
    return page


def _page_with_group(group: QGroupBox) -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(4, 4, 4, 4)
    layout.setSpacing(6)
    description = _group_description(group.title())
    if description:
        description_label = make_workflow_accent_label(description, "guide")
        description_label.setProperty("data_io_group_description", True)
        layout.addWidget(description_label)
    group.setParent(page)
    layout.addWidget(group)
    layout.addStretch(1)
    group.show()
    return page


def _group_description(group_title: str) -> str:
    if group_title.startswith("データ入出力 実行ログ"):
        return DATA_IO_LOG_DESCRIPTION
    group_key = group_title.split("（", maxsplit=1)[0]
    return DATA_IO_GROUP_DESCRIPTIONS.get(group_key, "")


def _insert_result_hint(root_layout: QVBoxLayout, widget: QWidget) -> None:
    result_view = getattr(widget, "result_view", None)
    if not isinstance(result_view, QWidget):
        return
    for index in range(root_layout.count()):
        item = root_layout.itemAt(index)
        if item is None:
            continue
        if item.widget() is result_view:
            hint = make_workflow_accent_label(DATA_IO_RESULT_DESCRIPTION, "guide")
            hint.setProperty("data_io_result_hint", True)
            root_layout.insertWidget(index, hint)
            return


def _take_first_grid_layout(root_layout: QVBoxLayout) -> tuple[int, QGridLayout | None]:
    for index in range(root_layout.count()):
        item = root_layout.itemAt(index)
        if item is None:
            continue
        layout = item.layout()
        if isinstance(layout, QGridLayout):
            root_layout.takeAt(index)
            return index, layout
    return -1, None


def _take_group_boxes_from_grid(grid: QGridLayout) -> dict[str, QGroupBox]:
    groups: dict[str, QGroupBox] = {}
    for index in reversed(range(grid.count())):
        item = grid.itemAt(index)
        if item is None:
            continue
        group = item.widget()
        if isinstance(group, QGroupBox):
            group.hide()
            grid.removeWidget(group)
            groups[group.title()] = group
    return groups


def _take_group_box_by_title(layout: QLayout, title_prefix: str) -> QGroupBox | None:
    for index in range(layout.count()):
        item = layout.itemAt(index)
        if item is None:
            continue
        group = item.widget()
        if isinstance(group, QGroupBox) and group.title().startswith(title_prefix):
            group.hide()
            layout.takeAt(index)
            return group
    return None

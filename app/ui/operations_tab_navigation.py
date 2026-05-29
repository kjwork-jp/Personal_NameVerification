"""Navigation restructuring helpers for the Operations tab."""

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

from app.ui.operations_guidance import DATA_IO_PAGE_DESCRIPTION, DATA_IO_PAGE_TITLE
from app.ui.ui_style import PageHeader

_GUIDE_TEXT_BY_ROLE = {
    "viewer": """
データ入出力タブの操作ガイド（viewer）

この権限では、実行ログの参照のみ利用できます。
Export / Backup / Restore / Import は表示しません。

1. Operations Log
   データ入出力タブの実行ログを確認・絞り込みできます。
   ログエクスポートは出力操作のため、viewerでは利用できません。

補足:
   viewerは参照専用です。DB更新、出力、バックアップ、復元、取込は行えません。
""".strip(),
    "editor": """
データ入出力タブの操作ガイド（editor）

この権限では、通常の出力とバックアップのみ利用できます。
Restore / Import は破壊的操作のため表示しません。

1. Export
   CSV / JSON / SQL dump を出力します。

2. Backup
   現在のSQLite DBをバックアップします。

3. Operations Log
   データ入出力タブの実行ログを確認・絞り込み・エクスポートします。

補足:
   editorは通常作業向けです。DB置換や外部データ取込はadminで実行してください。
""".strip(),
    "admin": """
データ入出力タブの操作ガイド（admin）

この権限では、データ入出力の全操作を利用できます。
Restore / Import は破壊的操作のため、実行前に必ずバックアップを取得してください。

1. Export
   CSV / JSON / SQL dump を出力します。

2. Backup
   現在のSQLite DBをバックアップします。

3. Restore
   バックアップDBで対象DBを置換します。destructive操作です。

4. Import
   CSV / JSON からDBへ取り込みます。destructive操作です。

5. Operations Log
   データ入出力タブの実行ログを確認・絞り込み・エクスポートします。
""".strip(),
}


def apply_operations_subtabs(widget: QWidget) -> None:
    """Reorganize the already-built OperationsTab into task-oriented subtabs.

    The existing OperationsTab owns all widgets and behavior. This helper only moves
    its grouped UI sections into a QTabWidget so the public widget attributes,
    signal connections, history handling, and RBAC guards remain unchanged.
    """

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

    logs_group = _take_group_box_by_title(root_layout, "Operations 実行ログ")

    sub_tabs = QTabWidget(widget)
    sub_tabs.setObjectName("operationsSubTabs")
    role = str(getattr(widget, "_role", "admin"))
    sub_tabs.addTab(_build_guide_page(role), "ガイド")

    section_order = [
        ("Export", "Export"),
        ("Backup", "Backup"),
        ("Restore（destructive）", "Restore"),
        ("Import（destructive）", "Import"),
    ]
    for group_title, tab_title in section_order:
        group = groups.get(group_title)
        if group is not None:
            sub_tabs.addTab(_page_with_group(group), tab_title)

    if logs_group is not None:
        sub_tabs.addTab(_page_with_group(logs_group), "Operations Log")

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
    group.setParent(page)
    layout.addWidget(group)
    layout.addStretch(1)
    group.show()
    return page


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

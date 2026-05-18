"""Unified title/subtitle management tab."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QLabel, QTabWidget, QVBoxLayout, QWidget

from app.ui.role_context import RoleContext
from app.ui.subtitle_management_tab import SubtitleManagementTab
from app.ui.title_management_tab import TitleManagementTab
from app.ui.ui_style import PageHeader, compact_layout


class TitleSubtitleUnifiedTab(QWidget):
    """Top-level container for title and subtitle management workflows."""

    def __init__(
        self,
        core_service: Any,
        query_service: Any,
        role_context: RoleContext | None = None,
    ) -> None:
        super().__init__()
        self.title_tab = TitleManagementTab(
            core_service=core_service,
            query_service=query_service,
            role_context=role_context,
        )
        self.subtitle_tab = SubtitleManagementTab(
            core_service=core_service,
            query_service=query_service,
            role_context=role_context,
        )

        self.tabs = QTabWidget()
        self.tabs.setObjectName("titleSubtitleSubTabs")
        self.tabs.addTab(self.title_tab, "タイトル")
        self.tabs.addTab(self.subtitle_tab, "サブタイトル")
        self.tabs.addTab(_build_guide_page(), "ガイド")

        root = QVBoxLayout(self)
        compact_layout(root, margins=5, spacing=4)
        root.addWidget(
            PageHeader(
                "タイトル/サブタイトル管理",
                "親マスタのタイトルと、配下のサブタイトルを一つの画面で管理します。",
            )
        )
        root.addWidget(self.tabs, 1)

    @property
    def editor(self) -> Any:
        """Expose the active child editor for existing refresh helpers."""

        current = self.tabs.currentWidget()
        return getattr(current, "editor", None)

    def refresh(self) -> None:
        """Refresh the currently visible title/subtitle child tab."""

        editor = self.editor
        if editor is not None:
            method = getattr(editor, "_refresh_titles", None)
            if callable(method):
                method()


def _build_guide_page() -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    compact_layout(layout, margins=8, spacing=6)
    text = QLabel(
        "タイトル: 名前に紐づく親マスタを登録・更新します。\n"
        "サブタイトル: 選択したタイトル配下の管理番号・サブタイトル名・表示順を登録・更新します。\n"
        "復元と完全削除は削除データタブに集約しています。"
    )
    text.setWordWrap(True)
    layout.addWidget(text)
    layout.addStretch(1)
    return page

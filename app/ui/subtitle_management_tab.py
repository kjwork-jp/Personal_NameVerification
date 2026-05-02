"""Focused subtitle management tab."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.ui.role_context import RoleContext
from app.ui.title_subtitle_management_tab import TitleSubtitleManagementTab
from app.ui.ui_style import PageHeader


class SubtitleManagementTab(QWidget):
    """Subtitle-focused wrapper around the existing title/subtitle editor.

    This is an incremental UI split. The underlying editor is still shared for
    compatibility, but the title creation form is hidden so users first choose a
    title and then manage its subtitles.
    """

    def __init__(
        self,
        core_service: Any,
        query_service: Any,
        role_context: RoleContext | None = None,
    ) -> None:
        super().__init__()
        self.editor = TitleSubtitleManagementTab(
            core_service=core_service,
            query_service=query_service,
            role_context=role_context,
        )
        self._hide_title_creation_controls()
        self._rename_labels()

        layout = QVBoxLayout(self)
        layout.addWidget(
            PageHeader(
                "サブタイトルを管理",
                "最初にタイトルを選び、そのタイトルに属するサブタイトルを登録・更新します。"
                "管理番号や表示順は将来的に自動化する予定です。",
            )
        )
        layout.addWidget(self.editor)

    def _hide_title_creation_controls(self) -> None:
        for widget in [
            self.editor.title_name_input,
            self.editor.title_note_input,
            self.editor.title_link_names_list,
            self.editor.linked_names_label,
            self.editor.title_create_button,
            self.editor.title_update_button,
            self.editor.title_delete_button,
            self.editor.title_restore_button,
            self.editor.title_hard_delete_button,
        ]:
            widget.hide()

    def _rename_labels(self) -> None:
        replacements = {
            "サブタイトル": "サブタイトル情報",
            "コード": "管理番号（自動化予定）",
            "sort_order": "表示順",
            "選択中タイトル: 未選択": "選択中のタイトル: 未選択",
            "タイトルを選択するとサブタイトル操作が有効になります": "上の一覧からタイトルを選ぶと、サブタイトルを管理できます",
            "操作者ID": "操作者",
        }
        for label in self.editor.findChildren(QLabel):
            text = label.text()
            if text in replacements:
                label.setText(replacements[text])

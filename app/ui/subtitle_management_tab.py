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
        self._hide_internal_columns()
        self._rename_labels()
        self._add_guidance_tooltips()

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

    def _hide_internal_columns(self) -> None:
        self.editor.titles_table.setColumnHidden(0, True)
        self.editor.subtitles_table.setColumnHidden(0, True)
        self.editor.subtitles_table.setColumnHidden(1, True)

    def _rename_labels(self) -> None:
        replacements = {
            "タイトル": "タイトルを選択",
            "サブタイトル": "サブタイトル情報",
            "コード": "管理番号（自動化予定）",
            "sort_order": "表示順",
            "選択中タイトル: 未選択": "選択中のタイトル: 未選択",
            "操作者ID": "操作者",
        }
        long_hint = "タイトルを選択するとサブタイトル操作が有効になります"
        for label in self.editor.findChildren(QLabel):
            text = label.text()
            if text in replacements:
                label.setText(replacements[text])
            elif text == long_hint:
                label.setText("上の一覧からタイトルを選ぶと、サブタイトルを管理できます")
            elif text == "タイトル作成時に紐づける名前":
                label.hide()
            elif text.startswith("紐づき名前:"):
                label.hide()

    def _add_guidance_tooltips(self) -> None:
        self.editor.operator_input.setToolTip(
            "現在は変更履歴用に入力します。将来的には設定またはログイン情報から自動入力します。"
        )
        self.editor.subtitle_code_input.setToolTip(
            "現在は互換性のため残しています。将来的には自動生成に変更します。"
        )
        self.editor.subtitle_sort_order_input.setToolTip(
            "一覧での表示順です。未入力時は 0 として扱います。"
        )

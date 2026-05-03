"""Focused title management tab."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.ui.role_context import RoleContext
from app.ui.title_subtitle_management_tab import TitleSubtitleManagementTab
from app.ui.ui_style import PageHeader


class TitleManagementTab(QWidget):
    """Title-focused wrapper around the existing title/subtitle editor.

    This is an incremental UI split. The underlying editor is still shared for
    compatibility, but the subtitle-specific controls are hidden so users can
    focus on selecting names and registering titles.
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
        self._hide_subtitle_controls()
        self._hide_internal_columns()
        self._rename_labels()
        self._add_guidance_tooltips()

        layout = QVBoxLayout(self)
        layout.addWidget(
            PageHeader(
                "タイトルを管理",
                "最初に名前を選び、その名前に関連するタイトルを登録・更新します。"
                "内部IDやコードは通常操作では使いません。",
            )
        )
        layout.addWidget(self.editor)

    def _hide_subtitle_controls(self) -> None:
        for widget in [
            self.editor.selected_title_label,
            self.editor.subtitle_hint_label,
            self.editor.subtitle_code_input,
            self.editor.subtitle_name_input,
            self.editor.subtitle_sort_order_input,
            self.editor.subtitle_note_input,
            self.editor.subtitle_refresh_button,
            self.editor.subtitle_create_button,
            self.editor.subtitle_update_button,
            self.editor.subtitle_delete_button,
            self.editor.subtitle_restore_button,
            self.editor.subtitle_hard_delete_button,
            self.editor.subtitles_table,
        ]:
            widget.hide()

    def _hide_internal_columns(self) -> None:
        self.editor.titles_table.setColumnHidden(0, True)

    def _rename_labels(self) -> None:
        replacements = {
            "タイトル作成時に紐づける名前": "このタイトルを関連付ける名前",
            "紐づき名前: なし": "関連する名前: なし",
            "タイトル": "タイトル情報",
            "サブタイトル": "",
            "操作者ID": "操作者",
        }
        for label in self.editor.findChildren(QLabel):
            text = label.text()
            if text == "サブタイトル":
                label.hide()
            elif text in replacements:
                label.setText(replacements[text])
            elif text.startswith("紐づき名前:"):
                label.setText(text.replace("紐づき名前", "関連する名前"))

    def _add_guidance_tooltips(self) -> None:
        self.editor.operator_input.setToolTip(
            "現在は変更履歴用に入力します。将来的には設定またはログイン情報から自動入力します。"
        )
        self.editor.title_link_names_list.setToolTip(
            "タイトルに関連付ける名前を選択します。複数選択できます。"
        )

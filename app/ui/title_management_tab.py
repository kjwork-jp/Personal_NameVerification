"""Focused title management tab."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.ui.role_context import RoleContext
from app.ui.title_subtitle_management_tab import TitleSubtitleManagementTab
from app.ui.ui_style import PageHeader, apply_workflow_accent, compact_layout


class TitleManagementTab(QWidget):
    """Title-focused wrapper around the existing title/subtitle editor."""

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
        self._apply_title_workflow_accents()

        layout = QVBoxLayout(self)
        compact_layout(layout, margins=5, spacing=4)
        layout.addWidget(
            PageHeader("タイトルを管理", "名前を選び、関連するタイトルを登録・更新します。"),
            0,
        )
        layout.addWidget(self.editor, 1)
        self.setProperty("workflow_accented_layout", True)

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
            "タイトル作成時に紐づける名前": "関連付ける名前",
            "紐づき名前: なし": "関連する名前: なし",
            "タイトル": "タイトル情報",
            "サブタイトル": "",
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
        self.editor.title_link_names_list.setToolTip(
            "タイトルに関連付ける名前を選択します。複数選択できます。"
        )

    def _apply_title_workflow_accents(self) -> None:
        apply_workflow_accent(self.editor.workflow_hint_label, "guide")
        apply_workflow_accent(self.editor.title_panel_label, "list")
        apply_workflow_accent(self.editor.title_list_hint_label, "list")
        apply_workflow_accent(self.editor.title_refresh_button, "list")
        apply_workflow_accent(self.editor.title_create_button, "add")
        apply_workflow_accent(self.editor.title_update_button, "edit")
        apply_workflow_accent(self.editor.title_delete_button, "delete")
        apply_workflow_accent(self.editor.title_restore_button, "delete")
        apply_workflow_accent(self.editor.title_hard_delete_button, "delete")
        apply_workflow_accent(self.editor.title_detail_group, "edit")
        apply_workflow_accent(self.editor.selected_title_context_label, "edit")
        self.editor.setProperty("workflow_accented_layout", True)

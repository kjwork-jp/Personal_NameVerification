"""Focused subtitle management tab."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.ui.role_context import RoleContext
from app.ui.title_subtitle_management_tab import TitleSubtitleManagementTab
from app.ui.ui_style import PageHeader, apply_workflow_accent, compact_layout


class SubtitleManagementTab(QWidget):
    """Subtitle-focused wrapper around the existing title/subtitle editor."""

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
        self._apply_subtitle_workflow_accents()

        layout = QVBoxLayout(self)
        compact_layout(layout, margins=5, spacing=4)
        layout.addWidget(
            PageHeader("サブタイトルを管理", "タイトルを選び、配下のサブタイトルを登録・更新します。"),
            0,
        )
        layout.addWidget(self.editor, 1)
        self.setProperty("workflow_accented_layout", True)

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
            "コード": "管理番号",
            "sort_order": "表示順",
            "選択中タイトル: 未選択": "選択中タイトル: 未選択",
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
        self.editor.subtitle_code_input.setToolTip("未入力の場合は自動生成されます。")
        self.editor.subtitle_sort_order_input.setToolTip("一覧での表示順です。未入力時は 0 として扱います。")

    def _apply_subtitle_workflow_accents(self) -> None:
        apply_workflow_accent(self.editor.workflow_hint_label, "guide")
        apply_workflow_accent(self.editor.title_panel_label, "list")
        apply_workflow_accent(self.editor.title_list_hint_label, "list")
        apply_workflow_accent(self.editor.title_refresh_button, "list")
        apply_workflow_accent(self.editor.subtitle_refresh_button, "list")
        apply_workflow_accent(self.editor.subtitle_create_button, "add")
        apply_workflow_accent(self.editor.subtitle_update_button, "edit")
        apply_workflow_accent(self.editor.subtitle_delete_button, "delete")
        apply_workflow_accent(self.editor.subtitle_restore_button, "delete")
        apply_workflow_accent(self.editor.subtitle_hard_delete_button, "delete")
        apply_workflow_accent(self.editor.subtitle_group, "edit")
        apply_workflow_accent(self.editor.subtitle_panel_label, "edit")
        apply_workflow_accent(self.editor.subtitle_hint_label, "edit")
        self.editor.setProperty("workflow_accented_layout", True)

"""Focused subtitle management tab."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QCompleter, QGroupBox, QLabel, QVBoxLayout, QWidget

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
        self._make_title_selectors_searchable()
        self._connect_subtitle_state_refresh()
        self._apply_subtitle_workflow_accents()
        self._apply_subtitle_workflow_defaults()

        layout = QVBoxLayout(self)
        compact_layout(layout, margins=5, spacing=4)
        layout.addWidget(
            PageHeader("サブタイトルを管理", "タイトルを選び、配下のサブタイトルを登録・更新します。"),
            0,
        )
        layout.addWidget(self.editor, 1)
        self.setProperty("workflow_accented_layout", True)
        self.setProperty("focused_subtitle_only_layout", True)

    def _hide_title_creation_controls(self) -> None:
        for widget in [
            self.editor.title_name_input,
            self.editor.title_note_input,
            self.editor.add_title_name_input,
            self.editor.add_title_note_input,
            self.editor.add_title_link_name_combo,
            self.editor.title_link_name_combo,
            self.editor.title_link_names_list,
            self.editor.linked_names_label,
            self.editor.title_create_button,
            self.editor.title_update_button,
            self.editor.title_delete_button,
            self.editor.title_restore_button,
            self.editor.title_hard_delete_button,
            self.editor.delete_title_selector_combo,
        ]:
            widget.hide()
        for group in self.editor.findChildren(QGroupBox):
            if "タイトル" in group.title() and "サブタイトル" not in group.title():
                group.hide()
                group.setProperty("hiddenByFocusedSubtitleWrapper", True)
        self.editor.setProperty("title_controls_hidden_for_subtitle_focus", True)

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
            label.setWordWrap(True)
            label.setMinimumHeight(0)
            text = label.text()
            if text in replacements:
                label.setText(replacements[text])
            elif text == long_hint:
                label.setText("タイトルを選ぶと、サブタイトルを管理できます")
            elif text == "タイトル作成時に紐づける名前":
                label.hide()
            elif text.startswith("紐づき名前:"):
                label.hide()

    def _add_guidance_tooltips(self) -> None:
        self.editor.subtitle_code_input.setToolTip("未入力の場合は自動生成されます。")
        self.editor.subtitle_sort_order_input.setToolTip("一覧での表示順です。未入力時は 0 です。")
        self.editor.add_subtitle_title_combo.setToolTip(
            "入力すると、タイトル名・公開IDを部分一致で検索し、最初の候補を自動選択します。"
        )

    def _make_title_selectors_searchable(self) -> None:
        for combo in (self.editor.add_subtitle_title_combo, self.editor.title_selector_combo):
            self._make_combo_searchable(combo)
        self.editor.setProperty("searchable_title_selector_for_subtitle", True)

    def _make_combo_searchable(self, combo: QComboBox) -> None:
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        completer = combo.completer() or QCompleter(combo.model(), combo)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        combo.setCompleter(completer)
        line_edit = combo.lineEdit()
        if line_edit is not None:
            line_edit.textEdited.connect(
                lambda text, target=combo: self._select_matching_title(target, text)
            )

    def _connect_subtitle_state_refresh(self) -> None:
        self.editor.add_subtitle_title_combo.currentIndexChanged.connect(
            lambda _index: self.editor._update_action_states()
        )
        self.editor.title_selector_combo.currentIndexChanged.connect(
            lambda _index: self.editor._update_action_states()
        )
        self.editor.workflow_tabs.currentChanged.connect(
            lambda _index: self._ensure_practical_title_selection()
        )
        self.editor.setProperty("subtitle_create_state_refresh_connected", True)

    def _apply_subtitle_workflow_defaults(self) -> None:
        self._ensure_practical_title_selection()
        self.editor.setProperty("subtitle_auto_selects_first_title", True)
        self.editor.setProperty("subtitle_search_text_auto_selects_title", True)

    def _ensure_practical_title_selection(self) -> None:
        current = self.editor.workflow_tabs.currentWidget()
        if current is self.editor.add_tab:
            self._prefer_first_active_title_for_create()
        elif current in {self.editor.edit_tab, self.editor.delete_tab}:
            self._prefer_first_active_title_for_edit()
        self.editor._update_action_states()

    def _prefer_first_active_title_for_create(self) -> None:
        combo = self.editor.add_subtitle_title_combo
        if combo.currentData() is not None:
            return
        for index in range(1, combo.count()):
            if combo.itemData(index) is not None:
                combo.setCurrentIndex(index)
                return

    def _prefer_first_active_title_for_edit(self) -> None:
        if self.editor._selected_title is not None:
            return
        for row in self.editor._titles:
            if row.deleted_at is None:
                self.editor._select_title_by_id(row.id)
                return

    def _select_matching_title(self, combo: QComboBox, text: str) -> None:
        query = text.strip().casefold()
        if not query:
            return
        for index in range(1, combo.count()):
            label = combo.itemText(index).casefold()
            if query in label:
                combo.setCurrentIndex(index)
                if combo is self.editor.title_selector_combo:
                    title_id = combo.itemData(index)
                    if title_id is not None:
                        self.editor._select_title_by_id(int(title_id))
                self.editor._update_action_states()
                return

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
        for group in self.editor.findChildren(QGroupBox):
            if group.title() == "サブタイトル削除":
                apply_workflow_accent(group, "delete")
                group.setProperty("danger_operation_group", True)
        self.editor.setProperty("workflow_accented_layout", True)

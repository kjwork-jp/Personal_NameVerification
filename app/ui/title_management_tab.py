"""Focused title management tab."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

from app.ui.dialogs import confirm_destructive_action
from app.ui.navigation_polish import apply_workflow_tab_navigation
from app.ui.permissions import can_run_destructive_actions
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
        self.title_list_summary_label = self._build_title_list_summary_label()
        self.title_delete_target_summary = self._build_title_summary_label(
            heading="削除対象タイトル"
        )
        self._hide_subtitle_controls()
        self._hide_internal_columns()
        self._rename_labels()
        self._add_guidance_tooltips()
        self._wrap_guidance_labels()
        self._insert_title_list_summary()
        self._insert_delete_target_summary()
        self._connect_title_defaults()
        self._install_title_summary_refresh()
        self._install_title_delete_danger_copy()
        self._apply_title_workflow_accents()
        apply_workflow_tab_navigation(self.editor.workflow_tabs)
        self._ensure_title_selected_for_edit()
        self._refresh_title_summary_cards()
        self._update_title_list_summary()

        layout = QVBoxLayout(self)
        compact_layout(layout, margins=5, spacing=4)
        layout.addWidget(
            PageHeader("タイトルを管理", "名前を選び、関連するタイトルを登録・更新します。"),
            0,
        )
        layout.addWidget(self.editor, 1)
        self.setProperty("workflow_accented_layout", True)
        self.setProperty("focused_title_only_layout", True)
        self.setProperty("title_list_summary_counters", True)

    def _build_title_list_summary_label(self) -> QLabel:
        label = QLabel("一覧 0件 / 選択中 0件 / 有効 0件 / 削除済み 0件 / 関連名あり 0件")
        label.setWordWrap(True)
        label.setMinimumHeight(0)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setProperty("title_list_summary_counter", True)
        return label

    def _build_title_summary_label(self, *, heading: str) -> QLabel:
        label = QLabel(self._title_summary_text(None, heading=heading))
        label.setWordWrap(True)
        label.setMinimumHeight(0)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        return label

    def _hide_subtitle_controls(self) -> None:
        for widget in [
            self.editor.selected_title_label,
            self.editor.subtitle_hint_label,
            self.editor.add_subtitle_title_combo,
            self.editor.add_subtitle_code_input,
            self.editor.add_subtitle_name_input,
            self.editor.add_subtitle_sort_order_input,
            self.editor.add_subtitle_note_input,
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
            self.editor.delete_subtitle_selector_combo,
            self.editor.subtitles_table,
        ]:
            widget.hide()
        for group in self.editor.findChildren(QGroupBox):
            if "サブタイトル" in group.title():
                group.hide()
                group.setProperty("hiddenByFocusedTitleWrapper", True)
        self.editor.setProperty("subtitle_controls_hidden_for_title_focus", True)

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
        self.editor.title_link_names_list.setToolTip("タイトルに関連付ける名前を選択します。")

    def _wrap_guidance_labels(self) -> None:
        for label in self.editor.findChildren(QLabel):
            label.setWordWrap(True)
            label.setMinimumHeight(0)
        self.editor.workflow_hint_label.setText("一覧・新規追加・編集・削除を分けています。")
        self.editor.selected_title_context_label.setText(self._title_summary_text(None))
        self.editor.selected_title_context_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.editor.selected_title_context_label.setProperty("selected_title_summary_card", True)
        self.editor.title_detail_group.setMaximumHeight(220)
        self.editor.setProperty("title_guidance_labels_wrapped", True)

    def _insert_title_list_summary(self) -> None:
        layout = self.editor.list_tab.layout()
        if layout is not None:
            layout.insertWidget(2, self.title_list_summary_label)
        self.editor.setProperty("title_list_summary_counters", True)

    def _insert_delete_target_summary(self) -> None:
        self.title_delete_target_summary.setProperty("title_delete_target_summary_card", True)
        for group in self.editor.findChildren(QGroupBox):
            if group.title() == "タイトル削除":
                group_layout = group.layout()
                if group_layout is not None:
                    group_layout.insertWidget(0, self.title_delete_target_summary)
                return

    def _connect_title_defaults(self) -> None:
        self.editor.workflow_tabs.currentChanged.connect(
            lambda _index: self._ensure_title_selected_for_edit()
        )
        self.editor.setProperty("title_auto_selects_first_title", True)

    def _install_title_summary_refresh(self) -> None:
        original_update_selected_title_label = self.editor._update_selected_title_label
        original_refresh_titles = self.editor._refresh_titles

        def update_selected_title_label_with_split_summary(title: Any | None = None) -> None:
            original_update_selected_title_label(title)
            self._refresh_title_summary_cards()
            self._update_title_list_summary()

        def refresh_titles_with_list_summary(selected_title_id: int | None = None) -> None:
            original_refresh_titles(selected_title_id)
            self._update_title_list_summary()

        self.editor._update_selected_title_label = update_selected_title_label_with_split_summary
        self.editor._refresh_titles = refresh_titles_with_list_summary
        self.editor.titles_table.itemSelectionChanged.connect(
            lambda: self._refresh_title_summary_cards()
        )
        self.editor.titles_table.itemSelectionChanged.connect(
            lambda: self._update_title_list_summary()
        )
        self.editor.title_selector_combo.currentIndexChanged.connect(
            lambda _index: self._refresh_title_summary_cards()
        )
        self.editor.title_selector_combo.currentIndexChanged.connect(
            lambda _index: self._update_title_list_summary()
        )
        self.editor.delete_title_selector_combo.currentIndexChanged.connect(
            lambda _index: self._refresh_title_summary_cards()
        )
        self.editor.delete_title_selector_combo.currentIndexChanged.connect(
            lambda _index: self._update_title_list_summary()
        )
        self.editor.setProperty("title_summary_split", True)

    def _install_title_delete_danger_copy(self) -> None:
        self.editor.title_delete_button.setText("選択中タイトルをゴミ箱に入れる")
        self.editor.title_restore_button.setText("削除済みタイトルを復元")
        self.editor.title_hard_delete_button.setText("削除済みタイトルを完全削除")

        def mutate_title_with_target_copy(
            label: str,
            method_name: str,
            *,
            require_deleted: bool,
        ) -> None:
            if not can_run_destructive_actions(self.editor._role_context.role):
                self.editor._set_message(f"このロールではタイトル{label}できません", is_error=True)
                return
            selected = self.editor._require_selected_title()
            operator_id = self.editor._require_operator_id()
            if selected is None or operator_id is None:
                return
            if selected.deleted != require_deleted:
                self.editor._set_message("対象の状態が操作条件に合いません", is_error=True)
                return
            target = self._selected_title_detail()
            if not confirm_destructive_action(
                self.editor,
                self._title_destructive_dialog_title(label),
                self._title_destructive_confirmation_text(label, target, selected.id, method_name),
            ):
                return
            getattr(self.editor._core_service, method_name)(
                selected.id,
                operator_id=operator_id,
                role=self.editor._role_context.role,
            )
            self.editor._set_message(f"タイトルを{label}しました")
            self.editor._refresh_titles(None if method_name == "hard_delete_title" else selected.id)
            self._refresh_title_summary_cards()
            self._update_title_list_summary()

        self.editor._mutate_title = mutate_title_with_target_copy
        self.editor.setProperty("title_delete_danger_copy", True)

    def _ensure_title_selected_for_edit(self) -> None:
        current = self.editor.workflow_tabs.currentWidget()
        if current not in {self.editor.edit_tab, self.editor.delete_tab}:
            return
        if self.editor._selected_title is not None:
            return
        for row in self.editor._titles:
            if row.deleted_at is None:
                self.editor._select_title_by_id(row.id)
                return

    def _selected_title_detail(self) -> Any | None:
        selected = self.editor._selected_title
        if selected is None:
            return None
        for row in self.editor._titles:
            if row.id == selected.id:
                return row
        return None

    def _refresh_title_summary_cards(self) -> None:
        title = self._selected_title_detail()
        self.editor.selected_title_context_label.setText(self._title_summary_text(title))
        self.title_delete_target_summary.setText(
            self._title_summary_text(title, heading="削除対象タイトル")
        )

    def _update_title_list_summary(self) -> None:
        total = len(self.editor._titles)
        deleted = sum(1 for row in self.editor._titles if row.deleted_at)
        active = total - deleted
        selected_count = 1 if self.editor._selected_title is not None else 0
        linked_title_count = sum(
            1 for row in self.editor._titles if self.editor._linked_names_text(row.id)
        )
        self.title_list_summary_label.setText(
            f"一覧 {total}件 / 選択中 {selected_count}件 / "
            f"有効 {active}件 / 削除済み {deleted}件 / 関連名あり {linked_title_count}件"
        )

    def _title_summary_text(self, title: Any | None, *, heading: str = "選択中タイトル") -> str:
        if title is None:
            return f"{heading}\nタイトル名  未選択\n公開ID      -\n状態        -\n関連名      -"
        state = "削除済み" if title.deleted_at else "有効"
        public_id = title.public_id or "未採番"
        linked_names = self.editor._linked_names_text(title.id) or "なし"
        return (
            f"{heading}\n"
            f"タイトル名  {title.title_name}\n"
            f"公開ID      {public_id}\n"
            f"状態        {state}\n"
            f"関連名      {linked_names}"
        )

    def _title_destructive_dialog_title(self, label: str) -> str:
        return f"タイトルを{label}確認"

    def _title_destructive_confirmation_text(
        self,
        label: str,
        title: Any | None,
        selected_id: int,
        method_name: str,
    ) -> str:
        title_name = title.title_name if title is not None else f"ID={selected_id}"
        public_id = (title.public_id or "未採番") if title is not None else "-"
        state = "削除済み" if title is not None and title.deleted_at else "有効"
        risk = "この操作は元に戻せません。" if method_name == "hard_delete_title" else ""
        if method_name == "delete_title":
            risk = "通常の編集対象から外れます。必要に応じて後で復元できます。"
        elif method_name == "restore_title":
            risk = "復元後は通常の編集対象に戻ります。"
        return (
            f"対象タイトル: {title_name}\n"
            f"公開ID: {public_id}\n"
            f"状態: {state}\n"
            f"操作: {label}\n"
            f"注意: {risk}\n\n"
            "実行してよろしいですか？"
        )

    def _apply_title_workflow_accents(self) -> None:
        apply_workflow_accent(self.editor.workflow_hint_label, "guide")
        apply_workflow_accent(self.editor.title_panel_label, "list")
        apply_workflow_accent(self.editor.title_list_hint_label, "list")
        apply_workflow_accent(self.editor.title_refresh_button, "list")
        apply_workflow_accent(self.title_list_summary_label, "list")
        apply_workflow_accent(self.editor.title_create_button, "add")
        apply_workflow_accent(self.editor.title_update_button, "edit")
        apply_workflow_accent(self.editor.title_delete_button, "delete")
        apply_workflow_accent(self.editor.title_restore_button, "delete")
        apply_workflow_accent(self.editor.title_hard_delete_button, "delete")
        apply_workflow_accent(self.editor.title_detail_group, "edit")
        apply_workflow_accent(self.editor.selected_title_context_label, "edit")
        apply_workflow_accent(self.title_delete_target_summary, "delete")
        for group in self.editor.findChildren(QGroupBox):
            if group.title() == "タイトル削除":
                apply_workflow_accent(group, "delete")
                group.setProperty("danger_operation_group", True)
        self.editor.setProperty("workflow_accented_layout", True)

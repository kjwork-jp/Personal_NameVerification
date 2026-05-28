"""Focused subtitle management tab."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QCompleter,
    QGroupBox,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.ui.public_id_display import short_public_id
from app.ui.role_context import RoleContext
from app.ui.title_subtitle_management_tab import TitleSubtitleManagementTab, _call_with_optional_role
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
        self.parent_summary_add = self._build_parent_summary_label()
        self.parent_summary_edit = self._build_parent_summary_label()
        self.parent_summary_remove = self._build_parent_summary_label()
        self.subtitle_summary_edit = self._build_subtitle_summary_label()
        self.subtitle_summary_remove = self._build_subtitle_summary_label()
        self._hide_title_creation_controls()
        self._hide_internal_columns()
        self._rename_labels()
        self._add_guidance_tooltips()
        self._make_title_selectors_searchable()
        self._replace_list_tab_with_subtitle_list()
        self._insert_parent_summary_cards()
        self._insert_subtitle_summary_cards()
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

    def _build_parent_summary_label(self) -> QLabel:
        label = QLabel(self._parent_summary_text(None))
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setProperty("parent_title_summary_card", True)
        return label

    def _build_subtitle_summary_label(self) -> QLabel:
        label = QLabel(self._subtitle_summary_text(None))
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setProperty("selected_subtitle_summary_card", True)
        return label

    def _insert_parent_summary_cards(self) -> None:
        add_layout = self.editor.add_tab.layout()
        edit_layout = self.editor.edit_tab.layout()
        remove_layout = self.editor.delete_tab.layout()
        if add_layout is not None:
            add_layout.insertWidget(1, self.parent_summary_add)
        if edit_layout is not None:
            edit_layout.insertWidget(1, self.parent_summary_edit)
        if remove_layout is not None:
            remove_layout.insertWidget(1, self.parent_summary_remove)
        self.editor.setProperty("parent_title_summary_cards", True)

    def _insert_subtitle_summary_cards(self) -> None:
        edit_layout = self.editor.edit_tab.layout()
        remove_layout = self.editor.delete_tab.layout()
        if edit_layout is not None:
            edit_layout.insertWidget(2, self.subtitle_summary_edit)
        if remove_layout is not None:
            remove_layout.insertWidget(2, self.subtitle_summary_remove)
        self.editor.setProperty("selected_subtitle_summary_cards", True)

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

    def _replace_list_tab_with_subtitle_list(self) -> None:
        subtitle_list_tab = self._build_subtitle_list_tab()
        index = self.editor.workflow_tabs.indexOf(self.editor.list_tab)
        if index >= 0:
            self.editor.workflow_tabs.removeTab(index)
            self.editor.workflow_tabs.insertTab(index, subtitle_list_tab, "一覧")
            self.editor.workflow_tabs.setCurrentIndex(index)
        self.editor.list_tab = subtitle_list_tab
        self._refresh_subtitle_list()
        self.editor.setProperty("subtitle_list_tab_replaced", True)

    def _build_subtitle_list_tab(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        compact_layout(layout, margins=2, spacing=4)
        label = QLabel("一覧: 登録済みサブタイトルを親タイトル別に確認します。")
        label.setWordWrap(True)
        self.subtitle_list_table = QTableWidget(0, 8)
        self.subtitle_list_table.setHorizontalHeaderLabels(
            ["公開ID", "親タイトル", "管理番号", "サブタイトル名", "状態", "表示順", "更新日時", "備考"]
        )
        self.subtitle_list_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.subtitle_list_refresh_button = QPushButton("サブタイトル一覧を再読込")
        self.subtitle_list_refresh_button.clicked.connect(self._refresh_subtitle_list_from_source)
        layout.addWidget(label)
        layout.addWidget(self.subtitle_list_table, 1)
        layout.addWidget(self.subtitle_list_refresh_button)
        return panel

    def _refresh_subtitle_list_from_source(self) -> None:
        selected = self.editor._selected_title.id if self.editor._selected_title else None
        self.editor._refresh_titles(selected)
        self._refresh_subtitle_list()
        self._ensure_practical_title_selection()

    def _refresh_subtitle_list(self) -> None:
        rows: list[tuple[str, str, str, str, str, str, str, str]] = []
        for title in self.editor._titles:
            try:
                subtitles = _call_with_optional_role(
                    self.editor._query_service.list_subtitles,
                    title.id,
                    role=self.editor._role_context.role,
                    include_deleted=True,
                )
            except Exception as exc:  # noqa: BLE001
                self.editor._set_message(f"サブタイトル一覧取得に失敗しました: {exc}", is_error=True)
                return
            for subtitle in subtitles:
                rows.append(
                    (
                        short_public_id(subtitle.public_id),
                        title.title_name,
                        subtitle.subtitle_code,
                        subtitle.subtitle_name,
                        "削除済み" if subtitle.deleted_at else "有効",
                        str(subtitle.sort_order),
                        subtitle.updated_at,
                        subtitle.note or "",
                    )
                )
        self.subtitle_list_table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                self.subtitle_list_table.setItem(row_index, column_index, QTableWidgetItem(value))
        self.subtitle_list_table.resizeColumnsToContents()

    def _connect_subtitle_state_refresh(self) -> None:
        self.editor.add_subtitle_title_combo.currentIndexChanged.connect(
            lambda _index: self._on_parent_title_changed()
        )
        self.editor.title_selector_combo.currentIndexChanged.connect(
            lambda _index: self._on_parent_title_changed()
        )
        self.editor.subtitles_table.itemSelectionChanged.connect(
            lambda: self._update_subtitle_summary_cards()
        )
        self.editor.delete_subtitle_selector_combo.currentIndexChanged.connect(
            lambda _index: self._update_subtitle_summary_cards()
        )
        self.editor.workflow_tabs.currentChanged.connect(
            lambda _index: self._ensure_practical_title_selection()
        )
        self.editor.subtitle_create_button.clicked.connect(lambda: self._refresh_subtitle_list())
        self.editor.subtitle_update_button.clicked.connect(lambda: self._refresh_subtitle_list())
        self.editor.setProperty("subtitle_create_state_refresh_connected", True)

    def _apply_subtitle_workflow_defaults(self) -> None:
        self._ensure_practical_title_selection()
        self._update_parent_summary_cards()
        self._update_subtitle_summary_cards()
        self.editor.setProperty("subtitle_auto_selects_first_title", True)
        self.editor.setProperty("subtitle_search_text_auto_selects_title", True)

    def _ensure_practical_title_selection(self) -> None:
        current = self.editor.workflow_tabs.currentWidget()
        if current is self.editor.add_tab:
            self._prefer_first_active_title_for_create()
        elif current in {self.editor.edit_tab, self.editor.delete_tab}:
            self._prefer_first_active_title_for_edit()
        self._update_parent_summary_cards()
        self._update_subtitle_summary_cards()
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

    def _on_parent_title_changed(self) -> None:
        self._update_parent_summary_cards()
        self._update_subtitle_summary_cards()
        self.editor._update_action_states()

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
                self._update_parent_summary_cards()
                self._update_subtitle_summary_cards()
                self.editor._update_action_states()
                return

    def _update_parent_summary_cards(self) -> None:
        create_title = self._title_by_id(self.editor.add_subtitle_title_combo.currentData())
        selected_title = self._selected_title_detail()
        fallback_title = selected_title or create_title
        self.parent_summary_add.setText(self._parent_summary_text(create_title))
        self.parent_summary_edit.setText(self._parent_summary_text(fallback_title))
        self.parent_summary_remove.setText(self._parent_summary_text(fallback_title))
        self.editor.setProperty("parent_title_summary_split", True)

    def _update_subtitle_summary_cards(self) -> None:
        selected = self._selected_subtitle_detail()
        self.subtitle_summary_edit.setText(self._subtitle_summary_text(selected))
        self.subtitle_summary_remove.setText(self._subtitle_summary_text(selected))
        self.editor.setProperty("selected_subtitle_summary_split", True)

    def _selected_title_detail(self) -> Any | None:
        selected = self.editor._selected_title
        if selected is None:
            return None
        return self._title_by_id(selected.id)

    def _selected_subtitle_detail(self) -> Any | None:
        selected = self.editor._selected_subtitle
        if selected is not None:
            return self._subtitle_by_id(selected.id)
        subtitle_id = self.editor.delete_subtitle_selector_combo.currentData()
        return self._subtitle_by_id(subtitle_id)

    def _title_by_id(self, title_id: object) -> Any | None:
        if title_id is None:
            return None
        for title in self.editor._titles:
            if title.id == int(title_id):
                return title
        return None

    def _subtitle_by_id(self, subtitle_id: object) -> Any | None:
        if subtitle_id is None:
            return None
        for subtitle in self.editor._subtitles:
            if subtitle.id == int(subtitle_id):
                return subtitle
        return None

    def _parent_summary_text(self, title: Any | None) -> str:
        if title is None:
            return "親タイトル\nタイトル名  未選択\n公開ID      -\n状態        -"
        state = "削除済み" if title.deleted_at else "有効"
        public_id = title.public_id or "未採番"
        return (
            "親タイトル\n"
            f"タイトル名  {title.title_name}\n"
            f"公開ID      {public_id}\n"
            f"状態        {state}"
        )

    def _subtitle_summary_text(self, subtitle: Any | None) -> str:
        if subtitle is None:
            return "選択中サブタイトル\n管理番号  未選択\n名称      -\n状態      -"
        state = "削除済み" if subtitle.deleted_at else "有効"
        return (
            "選択中サブタイトル\n"
            f"管理番号  {subtitle.subtitle_code}\n"
            f"名称      {subtitle.subtitle_name}\n"
            f"状態      {state}"
        )

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
        apply_workflow_accent(self.subtitle_list_refresh_button, "list")
        for label in (
            self.parent_summary_add,
            self.parent_summary_edit,
            self.parent_summary_remove,
            self.subtitle_summary_edit,
            self.subtitle_summary_remove,
        ):
            apply_workflow_accent(label, "guide")
        for group in self.editor.findChildren(QGroupBox):
            if group.title() == "サブタイトル削除":
                apply_workflow_accent(group, "delete")
                group.setProperty("danger_operation_group", True)
        self.editor.setProperty("workflow_accented_layout", True)

"""Name management tab UI (name entity only)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.application.core_services import NameInput
from app.application.read_models import NameDetail, NameSearchRow
from app.ui.dialogs import confirm_destructive_action
from app.ui.input_defaults import default_operator_id, friendly_error_message
from app.ui.permissions import can_create_or_update, can_run_destructive_actions
from app.ui.public_id_display import short_public_id
from app.ui.role_context import RoleContext, UserRole
from app.ui.ui_style import PageHeader, apply_readable_table, compact_layout, set_status_message


class NameWriteService(Protocol):
    def create_name(
        self,
        payload: NameInput,
        operator_id: str,
        role: UserRole = "admin",
    ) -> int: ...

    def update_name(
        self,
        name_id: int,
        payload: NameInput,
        operator_id: str,
        role: UserRole = "admin",
    ) -> None: ...

    def delete_name(
        self,
        name_id: int,
        operator_id: str,
        role: UserRole = "admin",
    ) -> None: ...

    def restore_name(
        self,
        name_id: int,
        operator_id: str,
        role: UserRole = "admin",
    ) -> None: ...

    def hard_delete_name(
        self,
        name_id: int,
        operator_id: str,
        role: UserRole = "admin",
    ) -> None: ...


class NameReadService(Protocol):
    def search_names(
        self,
        query: str | None = None,
        role: UserRole = "admin",
        *,
        exact_match: bool = False,
        title_id: int | None = None,
        has_links: bool | None = None,
        include_deleted: bool = False,
    ) -> list[NameSearchRow]: ...

    def get_name_detail(
        self,
        name_id: int,
        role: UserRole = "admin",
    ) -> NameDetail: ...


@dataclass(frozen=True)
class _SelectedName:
    id: int
    deleted: bool


_ACCENT_STYLES = {
    "list": ("#dbeafe", "#172554", "#60a5fa"),
    "add": ("#dcfce7", "#14532d", "#4ade80"),
    "edit": ("#e0e7ff", "#312e81", "#818cf8"),
    "delete": ("#fee2e2", "#7f1d1d", "#f87171"),
    "guide": ("#f3e8ff", "#581c87", "#c084fc"),
}


class NameManagementTab(QWidget):
    """UI for name create/update/delete flows."""

    def __init__(
        self,
        core_service: NameWriteService,
        query_service: NameReadService,
        role_context: RoleContext | None = None,
    ) -> None:
        super().__init__()
        self._core_service = core_service
        self._query_service = query_service
        self._role_context = role_context or RoleContext.admin()
        self._rows: list[NameSearchRow] = []
        self._selected: _SelectedName | None = None

        self.operator_input = QLineEdit()
        self.operator_input.setText(default_operator_id())
        self.operator_input.setPlaceholderText("操作者（自動入力）")
        self.operator_input.setToolTip(
            "初期値は自動入力されます。必要な場合だけ変更してください。"
        )

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("名前・検索用表記・備考で絞り込み")
        self.filter_input.returnPressed.connect(self._refresh_list)

        self.raw_name_input = QLineEdit()
        self.raw_name_input.setPlaceholderText("編集する名前")
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("編集する備考")
        self.add_raw_name_input = QLineEdit()
        self.add_raw_name_input.setPlaceholderText("新規追加する名前")
        self.add_note_input = QLineEdit()
        self.add_note_input.setPlaceholderText("新規追加する備考")
        self.delete_name_selector = QComboBox()
        self.delete_name_selector.currentIndexChanged.connect(self._on_delete_combo_changed)

        self.message_label = QLabel("")
        self.workflow_hint_label = self._make_accent_label(
            "一覧・新規追加・編集・削除をタブで分離しています。"
            "新規追加は選択状態を持ち込みません。",
            "guide",
        )

        self.names_table = QTableWidget(0, 9)
        self.names_table.setHorizontalHeaderLabels(
            [
                "内部ID",
                "公開ID",
                "名前",
                "検索用表記",
                "状態",
                "タイトル関連数",
                "サブタイトル関連数",
                "関連合計",
                "備考",
            ]
        )
        self.names_table.setColumnHidden(0, True)
        apply_readable_table(self.names_table)
        self.names_table.itemSelectionChanged.connect(self._on_row_selected)

        self.refresh_button = QPushButton("一覧を再読込")
        self.create_button = QPushButton("名前を新規作成")
        self.update_button = QPushButton("名前を更新")
        self.delete_button = QPushButton("名前をゴミ箱に入れる")
        self.restore_button = QPushButton("復元")
        self.hard_delete_button = QPushButton("完全削除")
        self.restore_button.hide()
        self.hard_delete_button.hide()

        self.refresh_button.clicked.connect(self._refresh_list)
        self.create_button.clicked.connect(self._create_name)
        self.update_button.clicked.connect(self._update_name)
        self.delete_button.clicked.connect(self._delete_name)
        self.restore_button.clicked.connect(self._restore_name)
        self.hard_delete_button.clicked.connect(self._hard_delete_name)

        self.workflow_tabs = QTabWidget()
        self.workflow_tabs.setObjectName("nameWorkflowTabs")
        self.list_tab = self._build_list_tab()
        self.add_tab = self._build_add_tab()
        self.edit_tab = self._build_edit_tab()
        self.delete_tab = self._build_delete_tab()
        self.guide_tab = self._build_guide_tab()
        self.workflow_tabs.addTab(self.list_tab, "一覧")
        self.workflow_tabs.addTab(self.add_tab, "新規追加")
        self.workflow_tabs.addTab(self.edit_tab, "編集")
        self.workflow_tabs.addTab(self.delete_tab, "削除")
        self.workflow_tabs.addTab(self.guide_tab, "ガイド")
        self.workflow_tabs.currentChanged.connect(self._on_workflow_tab_changed)

        layout = QVBoxLayout(self)
        compact_layout(layout, margins=5, spacing=4)
        layout.addWidget(PageHeader("名前", "名前の登録・更新と関連数の確認を行います。"))
        layout.addWidget(self.workflow_hint_label)
        layout.addWidget(self.workflow_tabs, 1)
        layout.addWidget(self.message_label)
        self.setProperty("has_list_first_layout", True)
        self.setProperty("has_list_first_hint", True)
        self.setProperty("native_list_first_layout", True)
        self.setProperty("workflow_tabs_layout", True)

        self._apply_role_guards()
        self._refresh_list()

    def _build_list_tab(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        compact_layout(layout, margins=4, spacing=4)
        self.list_hint_label = self._make_accent_label(
            "一覧: 名前を確認します。選択しても新規追加フォームには影響しません。",
            "list",
        )
        layout.addWidget(self.list_hint_label)
        layout.addWidget(self.filter_input)
        layout.addWidget(self.names_table, 1)
        layout.addWidget(self.refresh_button)
        return panel

    def _build_add_tab(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        compact_layout(layout, margins=4, spacing=4)
        self.add_hint_label = self._make_accent_label(
            "新規追加: 過去の選択状態を使わず、空フォームから作成します。",
            "add",
        )
        form = QFormLayout()
        compact_layout(form, margins=2, spacing=3)
        form.addRow("操作者ID", self.operator_input)
        form.addRow("名前", self.add_raw_name_input)
        form.addRow("備考", self.add_note_input)
        layout.addWidget(self.add_hint_label)
        layout.addLayout(form)
        layout.addWidget(self.create_button)
        layout.addStretch(1)
        return panel

    def _build_edit_tab(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        compact_layout(layout, margins=4, spacing=4)
        self.edit_hint_label = self._make_accent_label(
            "編集: 一覧で対象を明示的に選択してから更新します。",
            "edit",
        )
        form = QFormLayout()
        compact_layout(form, margins=2, spacing=3)
        form.addRow("名前", self.raw_name_input)
        form.addRow("備考", self.note_input)
        layout.addWidget(self.edit_hint_label)
        layout.addLayout(form)
        layout.addWidget(self.update_button)
        layout.addStretch(1)
        return panel

    def _build_delete_tab(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        compact_layout(layout, margins=4, spacing=4)
        self.delete_hint_label = self._make_accent_label(
            "削除: admin向けの操作です。通常の新規追加・編集から隔離しています。",
            "delete",
        )
        form = QFormLayout()
        compact_layout(form, margins=2, spacing=3)
        form.addRow("対象", self.delete_name_selector)
        layout.addWidget(self.delete_hint_label)
        layout.addLayout(form)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.restore_button)
        layout.addWidget(self.hard_delete_button)
        layout.addStretch(1)
        return panel

    def _build_guide_tab(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        compact_layout(layout, margins=4, spacing=4)
        guide = QTextEdit()
        guide.setReadOnly(True)
        guide.setPlainText(
            "操作順\n"
            "1. 一覧: 登録済みの名前を確認します。\n"
            "2. 新規追加: 選択状態を使わず、空フォームから作成します。\n"
            "3. 編集: 一覧で対象を選択してから既存データを更新します。\n"
            "4. 削除: admin向けの削除操作を隔離しています。\n\n"
            "viewerは参照専用です。editorは新規追加と編集ができます。"
            "adminは削除系操作も実行できます。"
        )
        layout.addWidget(self._make_accent_label("ガイド: 操作ルール", "guide"))
        layout.addWidget(guide, 1)
        return panel

    def _make_accent_label(self, text: str, accent: str) -> QLabel:
        text_color, background_color, border_color = _ACCENT_STYLES[accent]
        hint = QLabel(text)
        hint.setObjectName("nativeListFirstWorkflowHint")
        hint.setProperty("accent", accent)
        hint.setWordWrap(True)
        hint.setStyleSheet(
            "QLabel#nativeListFirstWorkflowHint {"
            f"color: {text_color};"
            f"background-color: {background_color};"
            f"border: 1px solid {border_color};"
            "border-radius: 6px;"
            "padding: 4px 6px;"
            "font-weight: 600;"
            "}"
        )
        return hint

    def _on_workflow_tab_changed(self, index: int) -> None:
        if self.workflow_tabs.widget(index) is self.add_tab:
            self.add_raw_name_input.clear()
            self.add_note_input.clear()
            self._set_message("新規追加タブでは過去の選択状態を使いません")
        self._apply_role_guards()

    def _apply_role_guards(self) -> None:
        role = self._role_context.role
        can_write = can_create_or_update(role)
        can_destructive = can_run_destructive_actions(role)
        disabled = "このロールでは実行できません"
        readonly = "viewerは参照専用です。名前・備考は編集できません"

        self.operator_input.setEnabled(can_write or can_destructive)
        for widget in (
            self.raw_name_input,
            self.note_input,
            self.add_raw_name_input,
            self.add_note_input,
        ):
            widget.setEnabled(can_write)
            widget.setToolTip("入力できます" if can_write else readonly)

        has_selected = self._selected is not None
        selected_deleted = bool(self._selected and self._selected.deleted)
        self.create_button.setEnabled(can_write)
        self.update_button.setEnabled(can_write and has_selected and not selected_deleted)
        self.delete_button.setEnabled(can_destructive and has_selected and not selected_deleted)
        self.restore_button.setEnabled(False)
        self.hard_delete_button.setEnabled(False)
        self.create_button.setToolTip(
            disabled if not can_write else "新規追加タブの入力内容で作成します"
        )
        self.update_button.setToolTip(
            disabled if not can_write else "一覧で選択した行を更新します"
        )
        self.delete_button.setToolTip(
            disabled if not can_destructive else "選択行をゴミ箱に入れます"
        )
        self.restore_button.setToolTip("復元は削除データタブで行います")
        self.hard_delete_button.setToolTip("完全削除は削除データタブで行います")
        if not can_write:
            self._set_message("viewerは名前の追加・更新・削除を実行できません", is_error=True)

    def _refresh_list(self) -> None:
        try:
            self._rows = self._query_service.search_names(
                query=self.filter_input.text() or None,
                include_deleted=True,
                role=self._role_context.role,
            )
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"一覧取得に失敗しました: {exc}", is_error=True)
            return

        self.names_table.setRowCount(len(self._rows))
        self.delete_name_selector.blockSignals(True)
        self.delete_name_selector.clear()
        self.delete_name_selector.addItem("未選択", None)
        for i, row in enumerate(self._rows):
            self.names_table.setItem(i, 0, QTableWidgetItem(str(row.id)))
            self.names_table.setItem(i, 1, QTableWidgetItem(short_public_id(row.public_id)))
            self.names_table.setItem(i, 2, QTableWidgetItem(row.raw_name))
            self.names_table.setItem(i, 3, QTableWidgetItem(row.normalized_name))
            self.names_table.setItem(
                i,
                4,
                QTableWidgetItem("削除済み" if row.deleted_at else "有効"),
            )
            self.names_table.setItem(i, 5, QTableWidgetItem(str(row.title_related_count)))
            self.names_table.setItem(i, 6, QTableWidgetItem(str(row.subtitle_related_count)))
            self.names_table.setItem(i, 7, QTableWidgetItem(str(row.linked_count)))
            self.names_table.setItem(i, 8, QTableWidgetItem(row.note or ""))
            status = "削除済み" if row.deleted_at else "有効"
            self.delete_name_selector.addItem(f"{row.raw_name}（{status}）", row.id)
        self.delete_name_selector.blockSignals(False)
        self._selected = None
        self.names_table.clearSelection()
        self.raw_name_input.clear()
        self.note_input.clear()
        self._apply_role_guards()

    def _on_delete_combo_changed(self, index: int) -> None:
        name_id = self.delete_name_selector.itemData(index)
        if name_id is None:
            self._selected = None
            self._apply_role_guards()
            return
        self._select_name_by_id(int(name_id))

    def _select_name_by_id(self, name_id: int) -> None:
        for index, row in enumerate(self._rows):
            if row.id == name_id:
                self.names_table.blockSignals(True)
                self.names_table.selectRow(index)
                self.names_table.blockSignals(False)
                self._select_row(row)
                return
        self._selected = None
        self._apply_role_guards()

    def _on_row_selected(self) -> None:
        idx = self.names_table.currentRow()
        if idx < 0 or idx >= len(self._rows):
            self._selected = None
            self._apply_role_guards()
            return
        self._select_row(self._rows[idx])

    def _select_row(self, row: NameSearchRow) -> None:
        self._selected = _SelectedName(row.id, row.deleted_at is not None)
        self.raw_name_input.setText(row.raw_name)
        self._set_delete_combo_to_id(row.id)
        try:
            detail = self._query_service.get_name_detail(
                row.id,
                role=self._role_context.role,
            )
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"詳細取得に失敗しました: {exc}", is_error=True)
            return
        self.note_input.setText(detail.note or "")
        self._apply_role_guards()

    def _set_delete_combo_to_id(self, name_id: int) -> None:
        for index in range(self.delete_name_selector.count()):
            if self.delete_name_selector.itemData(index) == name_id:
                self.delete_name_selector.blockSignals(True)
                self.delete_name_selector.setCurrentIndex(index)
                self.delete_name_selector.blockSignals(False)
                return

    def _create_name(self) -> None:
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールでは新規作成できません", is_error=True)
            return
        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        try:
            self._core_service.create_name(
                self._current_payload(for_create=True),
                operator_id=operator_id,
                role=self._role_context.role,
            )
            self._set_message("新規作成しました")
            self.add_raw_name_input.clear()
            self.add_note_input.clear()
            self._refresh_list()
        except Exception as exc:  # noqa: BLE001
            self._set_message(friendly_error_message("名前の新規作成", exc), is_error=True)

    def _update_name(self) -> None:
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールでは更新できません", is_error=True)
            return
        selected = self._require_selected()
        operator_id = self._require_operator_id()
        if selected is None or operator_id is None:
            return
        if selected.deleted:
            self._set_message("削除済みは更新できません", is_error=True)
            return
        try:
            self._core_service.update_name(
                selected.id,
                self._current_payload(for_create=False),
                operator_id=operator_id,
                role=self._role_context.role,
            )
            self._set_message("更新しました")
            self._refresh_list()
        except Exception as exc:  # noqa: BLE001
            self._set_message(friendly_error_message("名前の更新", exc), is_error=True)

    def _delete_name(self) -> None:
        selected = self._require_selected()
        operator_id = self._require_operator_id()
        if selected is None or operator_id is None:
            return
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールでは論理削除できません", is_error=True)
            return
        if selected.deleted:
            self._set_message("既に削除済みです", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "ゴミ箱に入れる確認",
            f"名前ID={selected.id} をゴミ箱に入れます。よろしいですか？",
        ):
            self._set_message("ゴミ箱への移動をキャンセルしました")
            return
        self._core_service.delete_name(
            selected.id,
            operator_id=operator_id,
            role=self._role_context.role,
        )
        self._set_message("ゴミ箱に入れました")
        self._refresh_list()

    def _restore_name(self) -> None:
        selected = self._require_selected()
        operator_id = self._require_operator_id()
        if selected is None or operator_id is None:
            return
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールでは復元できません", is_error=True)
            return
        if not selected.deleted:
            self._set_message("有効行は復元できません", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "復元の確認",
            f"名前ID={selected.id} を復元します。よろしいですか？",
        ):
            self._set_message("復元をキャンセルしました")
            return
        self._core_service.restore_name(
            selected.id,
            operator_id=operator_id,
            role=self._role_context.role,
        )
        self._set_message("復元しました")
        self._refresh_list()

    def _hard_delete_name(self) -> None:
        selected = self._require_selected()
        operator_id = self._require_operator_id()
        if selected is None or operator_id is None:
            return
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールでは完全削除できません", is_error=True)
            return
        if not selected.deleted:
            self._set_message("完全削除は削除済み行のみ可能です", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "完全削除の確認",
            f"名前ID={selected.id} を完全削除します。この操作は元に戻せません。",
        ):
            self._set_message("完全削除をキャンセルしました")
            return
        self._core_service.hard_delete_name(
            selected.id,
            operator_id=operator_id,
            role=self._role_context.role,
        )
        self._set_message("完全削除しました")
        self._refresh_list()

    def _current_payload(self, *, for_create: bool | None = None) -> NameInput:
        create_mode = self.workflow_tabs.currentWidget() is self.add_tab
        if for_create is not None:
            create_mode = for_create
        if create_mode:
            raw_name = self.add_raw_name_input.text() or self.raw_name_input.text()
            note = self.add_note_input.text() or self.note_input.text()
            return NameInput(raw_name=raw_name, note=note or None)
        return NameInput(raw_name=self.raw_name_input.text(), note=self.note_input.text() or None)

    def _require_operator_id(self) -> str | None:
        operator_id = self.operator_input.text().strip()
        if not operator_id:
            self._set_message("操作者ID を入力してください", is_error=True)
            return None
        return operator_id

    def _require_selected(self) -> _SelectedName | None:
        if self._selected is None:
            self._on_row_selected()
        if self._selected is None:
            self._set_message("行を選択してください", is_error=True)
        return self._selected

    def _set_message(self, message: str, *, is_error: bool = False) -> None:
        set_status_message(self.message_label, message, level="error" if is_error else "success")

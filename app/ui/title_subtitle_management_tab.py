"""Title/Subtitle management tab UI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.application.core_services import SubtitleInput, TitleInput
from app.application.read_models import SubtitleDetail, TitleDetail
from app.ui.dialogs import confirm_destructive_action
from app.ui.permissions import can_create_or_update, can_run_destructive_actions
from app.ui.role_context import RoleContext


class TitleSubtitleWriteService(Protocol):
    def create_title(self, payload: TitleInput, operator_id: str) -> int: ...

    def update_title(self, title_id: int, payload: TitleInput, operator_id: str) -> None: ...

    def delete_title(self, title_id: int, operator_id: str) -> None: ...

    def restore_title(self, title_id: int, operator_id: str) -> None: ...

    def hard_delete_title(self, title_id: int, operator_id: str) -> None: ...

    def create_subtitle(self, payload: SubtitleInput, operator_id: str) -> int: ...

    def update_subtitle(
        self, subtitle_id: int, payload: SubtitleInput, operator_id: str
    ) -> None: ...

    def delete_subtitle(self, subtitle_id: int, operator_id: str) -> None: ...

    def restore_subtitle(self, subtitle_id: int, operator_id: str) -> None: ...

    def hard_delete_subtitle(self, subtitle_id: int, operator_id: str) -> None: ...


class TitleSubtitleReadService(Protocol):
    def list_titles(self, *, include_deleted: bool = False) -> list[TitleDetail]: ...

    def list_subtitles(
        self, title_id: int, *, include_deleted: bool = False
    ) -> list[SubtitleDetail]: ...


@dataclass(frozen=True)
class _TitleSelection:
    id: int
    deleted: bool


@dataclass(frozen=True)
class _SubtitleSelection:
    id: int
    deleted: bool


class TitleSubtitleManagementTab(QWidget):
    """UI for title/subtitle management flows."""

    def __init__(
        self,
        core_service: TitleSubtitleWriteService,
        query_service: TitleSubtitleReadService,
        role_context: RoleContext | None = None,
    ) -> None:
        super().__init__()
        self._core_service = core_service
        self._query_service = query_service
        self._role_context = role_context or RoleContext.admin()

        self._titles: list[TitleDetail] = []
        self._subtitles: list[SubtitleDetail] = []
        self._selected_title: _TitleSelection | None = None
        self._selected_subtitle: _SubtitleSelection | None = None

        self.operator_input = QLineEdit()
        self.operator_input.setPlaceholderText("operator_id")

        self.title_name_input = QLineEdit()
        self.title_note_input = QLineEdit()

        self.subtitle_code_input = QLineEdit()
        self.subtitle_name_input = QLineEdit()
        self.subtitle_sort_order_input = QLineEdit()
        self.subtitle_sort_order_input.setPlaceholderText("0")
        self.subtitle_note_input = QLineEdit()

        self.message_label = QLabel("")

        self.titles_table = QTableWidget(0, 3)
        self.titles_table.setHorizontalHeaderLabels(["ID", "タイトル", "状態"])
        self.titles_table.itemSelectionChanged.connect(self._on_title_selected)

        self.subtitles_table = QTableWidget(0, 4)
        self.subtitles_table.setHorizontalHeaderLabels(["ID", "コード", "サブタイトル", "状態"])
        self.subtitles_table.itemSelectionChanged.connect(self._on_subtitle_selected)

        self.title_refresh_button = QPushButton("タイトル再読込")
        self.title_refresh_button.clicked.connect(self._refresh_titles)
        self.title_create_button = QPushButton("タイトル作成")
        self.title_create_button.clicked.connect(self._create_title)
        self.title_update_button = QPushButton("タイトル更新")
        self.title_update_button.clicked.connect(self._update_title)
        self.title_delete_button = QPushButton("タイトル論理削除")
        self.title_delete_button.clicked.connect(self._delete_title)
        self.title_restore_button = QPushButton("タイトル復元")
        self.title_restore_button.clicked.connect(self._restore_title)
        self.title_hard_delete_button = QPushButton("タイトル完全削除")
        self.title_hard_delete_button.clicked.connect(self._hard_delete_title)

        self.subtitle_refresh_button = QPushButton("サブタイトル再読込")
        self.subtitle_refresh_button.clicked.connect(self._refresh_subtitles)
        self.subtitle_create_button = QPushButton("サブタイトル作成")
        self.subtitle_create_button.clicked.connect(self._create_subtitle)
        self.subtitle_update_button = QPushButton("サブタイトル更新")
        self.subtitle_update_button.clicked.connect(self._update_subtitle)
        self.subtitle_delete_button = QPushButton("サブタイトル論理削除")
        self.subtitle_delete_button.clicked.connect(self._delete_subtitle)
        self.subtitle_restore_button = QPushButton("サブタイトル復元")
        self.subtitle_restore_button.clicked.connect(self._restore_subtitle)
        self.subtitle_hard_delete_button = QPushButton("サブタイトル完全削除")
        self.subtitle_hard_delete_button.clicked.connect(self._hard_delete_subtitle)

        top_form = QFormLayout()
        top_form.addRow("operator_id", self.operator_input)

        title_form = QFormLayout()
        title_form.addRow("タイトル名", self.title_name_input)
        title_form.addRow("備考", self.title_note_input)

        title_actions = QHBoxLayout()
        for button in [
            self.title_refresh_button,
            self.title_create_button,
            self.title_update_button,
            self.title_delete_button,
            self.title_restore_button,
            self.title_hard_delete_button,
        ]:
            title_actions.addWidget(button)

        title_panel = QWidget()
        title_layout = QVBoxLayout(title_panel)
        title_layout.addWidget(QLabel("タイトル"))
        title_layout.addLayout(title_form)
        title_layout.addLayout(title_actions)
        title_layout.addWidget(self.titles_table)

        subtitle_form = QFormLayout()
        subtitle_form.addRow("コード", self.subtitle_code_input)
        subtitle_form.addRow("サブタイトル名", self.subtitle_name_input)
        subtitle_form.addRow("sort_order", self.subtitle_sort_order_input)
        subtitle_form.addRow("備考", self.subtitle_note_input)

        subtitle_actions = QHBoxLayout()
        for button in [
            self.subtitle_refresh_button,
            self.subtitle_create_button,
            self.subtitle_update_button,
            self.subtitle_delete_button,
            self.subtitle_restore_button,
            self.subtitle_hard_delete_button,
        ]:
            subtitle_actions.addWidget(button)

        subtitle_panel = QWidget()
        subtitle_layout = QVBoxLayout(subtitle_panel)
        subtitle_layout.addWidget(QLabel("サブタイトル"))
        subtitle_layout.addLayout(subtitle_form)
        subtitle_layout.addLayout(subtitle_actions)
        subtitle_layout.addWidget(self.subtitles_table)

        splitter = QSplitter()
        splitter.addWidget(title_panel)
        splitter.addWidget(subtitle_panel)

        root = QVBoxLayout(self)
        root.addLayout(top_form)
        root.addWidget(self.message_label)
        root.addWidget(splitter)

        self._apply_role_guards()
        self._refresh_titles()

    def _apply_role_guards(self) -> None:
        role = self._role_context.role
        can_write = can_create_or_update(role)
        can_destructive = can_run_destructive_actions(role)

        self.title_create_button.setEnabled(can_write)
        self.title_update_button.setEnabled(can_write)
        self.subtitle_create_button.setEnabled(can_write)
        self.subtitle_update_button.setEnabled(can_write)

        self.title_delete_button.setEnabled(can_destructive)
        self.title_restore_button.setEnabled(can_destructive)
        self.title_hard_delete_button.setEnabled(can_destructive)
        self.subtitle_delete_button.setEnabled(can_destructive)
        self.subtitle_restore_button.setEnabled(can_destructive)
        self.subtitle_hard_delete_button.setEnabled(can_destructive)

    def _refresh_titles(self) -> None:
        try:
            self._titles = self._query_service.list_titles(include_deleted=True)
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"タイトル一覧取得に失敗しました: {exc}", is_error=True)
            return

        self.titles_table.setRowCount(len(self._titles))
        for i, row in enumerate(self._titles):
            self.titles_table.setItem(i, 0, QTableWidgetItem(str(row.id)))
            self.titles_table.setItem(i, 1, QTableWidgetItem(row.title_name))
            self.titles_table.setItem(
                i, 2, QTableWidgetItem("削除済み" if row.deleted_at else "有効")
            )

        self._selected_title = None
        self._subtitles = []
        self.subtitles_table.setRowCount(0)
        if self._titles:
            self.titles_table.selectRow(0)

    def _refresh_subtitles(self) -> None:
        selected = self._require_selected_title()
        if selected is None:
            return

        try:
            self._subtitles = self._query_service.list_subtitles(selected.id, include_deleted=True)
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"サブタイトル一覧取得に失敗しました: {exc}", is_error=True)
            return

        self.subtitles_table.setRowCount(len(self._subtitles))
        for i, row in enumerate(self._subtitles):
            self.subtitles_table.setItem(i, 0, QTableWidgetItem(str(row.id)))
            self.subtitles_table.setItem(i, 1, QTableWidgetItem(row.subtitle_code))
            self.subtitles_table.setItem(i, 2, QTableWidgetItem(row.subtitle_name))
            self.subtitles_table.setItem(
                i, 3, QTableWidgetItem("削除済み" if row.deleted_at else "有効")
            )

        self._selected_subtitle = None

    def _on_title_selected(self) -> None:
        idx = self.titles_table.currentRow()
        if idx < 0 or idx >= len(self._titles):
            self._selected_title = None
            return

        selected = self._titles[idx]
        self._selected_title = _TitleSelection(
            id=selected.id, deleted=selected.deleted_at is not None
        )
        self.title_name_input.setText(selected.title_name)
        self.title_note_input.setText(selected.note or "")
        self._refresh_subtitles()

    def _on_subtitle_selected(self) -> None:
        idx = self.subtitles_table.currentRow()
        if idx < 0 or idx >= len(self._subtitles):
            self._selected_subtitle = None
            return

        selected = self._subtitles[idx]
        self._selected_subtitle = _SubtitleSelection(
            id=selected.id,
            deleted=selected.deleted_at is not None,
        )
        self.subtitle_code_input.setText(selected.subtitle_code)
        self.subtitle_name_input.setText(selected.subtitle_name)
        self.subtitle_sort_order_input.setText(str(selected.sort_order))
        self.subtitle_note_input.setText(selected.note or "")

    def _create_title(self) -> None:
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールではタイトル作成できません", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        try:
            self._core_service.create_title(self._title_payload(), operator_id=operator_id)
            self._set_message("タイトル作成しました")
            self._refresh_titles()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"タイトル作成に失敗しました: {exc}", is_error=True)

    def _update_title(self) -> None:
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールではタイトル更新できません", is_error=True)
            return

        selected = self._require_selected_title()
        if selected is None:
            return
        if selected.deleted:
            self._set_message("削除済みタイトルは更新できません", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return

        try:
            self._core_service.update_title(
                selected.id, self._title_payload(), operator_id=operator_id
            )
            self._set_message("タイトル更新しました")
            self._refresh_titles()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"タイトル更新に失敗しました: {exc}", is_error=True)

    def _delete_title(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールではタイトル論理削除できません", is_error=True)
            return

        selected = self._require_selected_title()
        if selected is None:
            return
        if selected.deleted:
            self._set_message("既に削除済みタイトルです", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return

        try:
            if not confirm_destructive_action(
                self,
                "論理削除の確認",
                f"タイトルID={selected.id} を論理削除します。よろしいですか？",
            ):
                self._set_message("タイトル論理削除をキャンセルしました")
                return
            self._core_service.delete_title(selected.id, operator_id=operator_id)
            self._set_message("タイトル論理削除しました")
            self._refresh_titles()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"タイトル論理削除に失敗しました: {exc}", is_error=True)

    def _restore_title(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールではタイトル復元できません", is_error=True)
            return

        selected = self._require_selected_title()
        if selected is None:
            return
        if not selected.deleted:
            self._set_message("有効タイトルは復元できません", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return

        try:
            if not confirm_destructive_action(
                self,
                "復元の確認",
                f"タイトルID={selected.id} を復元します。よろしいですか？",
            ):
                self._set_message("タイトル復元をキャンセルしました")
                return
            self._core_service.restore_title(selected.id, operator_id=operator_id)
            self._set_message("タイトル復元しました")
            self._refresh_titles()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"タイトル復元に失敗しました: {exc}", is_error=True)

    def _hard_delete_title(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールではタイトル完全削除できません", is_error=True)
            return

        selected = self._require_selected_title()
        if selected is None:
            return
        if not selected.deleted:
            self._set_message("完全削除は削除済みタイトルのみ可能です", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return

        try:
            if not confirm_destructive_action(
                self,
                "完全削除の確認",
                f"タイトルID={selected.id} を完全削除します。この操作は元に戻せません。",
            ):
                self._set_message("タイトル完全削除をキャンセルしました")
                return
            self._core_service.hard_delete_title(selected.id, operator_id=operator_id)
            self._set_message("タイトル完全削除しました")
            self._refresh_titles()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"タイトル完全削除に失敗しました: {exc}", is_error=True)

    def _create_subtitle(self) -> None:
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールではサブタイトル作成できません", is_error=True)
            return

        selected = self._require_selected_title()
        if selected is None:
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return

        try:
            self._core_service.create_subtitle(
                self._subtitle_payload(title_id=selected.id),
                operator_id=operator_id,
            )
            self._set_message("サブタイトル作成しました")
            self._refresh_subtitles()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"サブタイトル作成に失敗しました: {exc}", is_error=True)

    def _update_subtitle(self) -> None:
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールではサブタイトル更新できません", is_error=True)
            return

        selected_subtitle = self._require_selected_subtitle()
        selected_title = self._require_selected_title()
        if selected_subtitle is None or selected_title is None:
            return
        if selected_subtitle.deleted:
            self._set_message("削除済みサブタイトルは更新できません", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return

        try:
            self._core_service.update_subtitle(
                selected_subtitle.id,
                self._subtitle_payload(title_id=selected_title.id),
                operator_id=operator_id,
            )
            self._set_message("サブタイトル更新しました")
            self._refresh_subtitles()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"サブタイトル更新に失敗しました: {exc}", is_error=True)

    def _delete_subtitle(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールではサブタイトル論理削除できません", is_error=True)
            return

        selected = self._require_selected_subtitle()
        if selected is None:
            return
        if selected.deleted:
            self._set_message("既に削除済みサブタイトルです", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return

        try:
            if not confirm_destructive_action(
                self,
                "論理削除の確認",
                f"サブタイトルID={selected.id} を論理削除します。よろしいですか？",
            ):
                self._set_message("サブタイトル論理削除をキャンセルしました")
                return
            self._core_service.delete_subtitle(selected.id, operator_id=operator_id)
            self._set_message("サブタイトル論理削除しました")
            self._refresh_subtitles()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"サブタイトル論理削除に失敗しました: {exc}", is_error=True)

    def _restore_subtitle(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールではサブタイトル復元できません", is_error=True)
            return

        selected = self._require_selected_subtitle()
        if selected is None:
            return
        if not selected.deleted:
            self._set_message("有効サブタイトルは復元できません", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return

        try:
            if not confirm_destructive_action(
                self,
                "復元の確認",
                f"サブタイトルID={selected.id} を復元します。よろしいですか？",
            ):
                self._set_message("サブタイトル復元をキャンセルしました")
                return
            self._core_service.restore_subtitle(selected.id, operator_id=operator_id)
            self._set_message("サブタイトル復元しました")
            self._refresh_subtitles()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"サブタイトル復元に失敗しました: {exc}", is_error=True)

    def _hard_delete_subtitle(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールではサブタイトル完全削除できません", is_error=True)
            return

        selected = self._require_selected_subtitle()
        if selected is None:
            return
        if not selected.deleted:
            self._set_message("完全削除は削除済みサブタイトルのみ可能です", is_error=True)
            return

        operator_id = self._require_operator_id()
        if operator_id is None:
            return

        try:
            if not confirm_destructive_action(
                self,
                "完全削除の確認",
                f"サブタイトルID={selected.id} を完全削除します。この操作は元に戻せません。",
            ):
                self._set_message("サブタイトル完全削除をキャンセルしました")
                return
            self._core_service.hard_delete_subtitle(selected.id, operator_id=operator_id)
            self._set_message("サブタイトル完全削除しました")
            self._refresh_subtitles()
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"サブタイトル完全削除に失敗しました: {exc}", is_error=True)

    def _title_payload(self) -> TitleInput:
        return TitleInput(
            title_name=self.title_name_input.text(), note=self.title_note_input.text() or None
        )

    def _subtitle_payload(self, title_id: int) -> SubtitleInput:
        sort_order_text = self.subtitle_sort_order_input.text().strip() or "0"
        return SubtitleInput(
            title_id=title_id,
            subtitle_code=self.subtitle_code_input.text(),
            subtitle_name=self.subtitle_name_input.text(),
            sort_order=int(sort_order_text),
            note=self.subtitle_note_input.text() or None,
        )

    def _require_operator_id(self) -> str | None:
        operator_id = self.operator_input.text().strip()
        if not operator_id:
            self._set_message("operator_id を入力してください", is_error=True)
            return None
        return operator_id

    def _require_selected_title(self) -> _TitleSelection | None:
        if self._selected_title is None:
            self._set_message("タイトルを選択してください", is_error=True)
            return None
        return self._selected_title

    def _require_selected_subtitle(self) -> _SubtitleSelection | None:
        if self._selected_subtitle is None:
            self._set_message("サブタイトルを選択してください", is_error=True)
            return None
        return self._selected_subtitle

    def _set_message(self, message: str, *, is_error: bool = False) -> None:
        color = "#b00020" if is_error else "#0b6b0b"
        self.message_label.setStyleSheet(f"color: {color};")
        self.message_label.setText(message)

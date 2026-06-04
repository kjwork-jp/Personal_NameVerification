"""Trash tab UI for restoring/hard-deleting logically deleted entities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.application.read_models import NameDetail, RelatedRow, SubtitleDetail, TitleDetail
from app.ui.datetime_display import format_datetime_display
from app.ui.dialogs import confirm_destructive_action
from app.ui.input_defaults import default_operator_id
from app.ui.permissions import can_run_destructive_actions
from app.ui.public_id_display import short_public_id
from app.ui.role_context import RoleContext, UserRole
from app.ui.trash_tab_navigation import apply_trash_subtabs
from app.ui.ui_style import (
    PageHeader,
    apply_readable_table,
    apply_workflow_accent,
    compact_layout,
    make_workflow_accent_label,
)


class TrashReadService(Protocol):
    def list_deleted_names(self, role: UserRole = "admin") -> list[NameDetail]: ...

    def list_deleted_titles(self, role: UserRole = "admin") -> list[TitleDetail]: ...

    def list_deleted_subtitles(self, role: UserRole = "admin") -> list[SubtitleDetail]: ...

    def list_deleted_links(self, role: UserRole = "admin") -> list[RelatedRow]: ...


class TrashWriteService(Protocol):
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

    def restore_title(
        self,
        title_id: int,
        operator_id: str,
        role: UserRole = "admin",
    ) -> None: ...

    def hard_delete_title(
        self,
        title_id: int,
        operator_id: str,
        role: UserRole = "admin",
    ) -> None: ...

    def restore_subtitle(
        self,
        subtitle_id: int,
        operator_id: str,
        role: UserRole = "admin",
    ) -> None: ...

    def hard_delete_subtitle(
        self,
        subtitle_id: int,
        operator_id: str,
        role: UserRole = "admin",
    ) -> None: ...

    def restore_link(
        self,
        link_id: int,
        operator_id: str,
        role: UserRole = "admin",
    ) -> None: ...

    def hard_delete_link(
        self,
        link_id: int,
        operator_id: str,
        role: UserRole = "admin",
    ) -> None: ...


@dataclass(frozen=True)
class _TrashRow:
    entity_key: str
    entity_label: str
    entity_id: int
    public_id: str | None
    display_name: str
    title_name: str
    subtitle_code: str
    deleted_at: str | None
    detail: str


class TrashTab(QWidget):
    """Cross-entity trash UI."""

    def __init__(
        self,
        core_service: TrashWriteService,
        query_service: TrashReadService,
        role_context: RoleContext | None = None,
    ) -> None:
        super().__init__()
        self._core_service = core_service
        self._query_service = query_service
        self._role_context = role_context or RoleContext.admin()
        self._trash_rows: list[_TrashRow] = []
        self._selected: _TrashRow | None = None

        self.entity_selector = QComboBox()
        self.entity_selector.addItems(
            [
                "すべて",
                "名前",
                "タイトル",
                "サブタイトル",
                "リンク",
                "All",
                "Name",
                "Title",
                "Subtitle",
                "Link",
            ]
        )
        self.entity_selector.currentTextChanged.connect(self._reload)

        self.operator_input = QLineEdit(default_operator_id())
        self.operator_input.setPlaceholderText("操作者ID")
        self.operator_input.setToolTip("復元/完全削除の変更履歴に記録する操作者です。")
        self.message_label = QLabel("")

        self.list_table = QTableWidget(0, 8)
        self.list_table.setHorizontalHeaderLabels(
            [
                "内部ID",
                "分類",
                "公開ID",
                "表示名",
                "タイトル",
                "管理番号",
                "削除日時",
                "詳細",
            ]
        )
        self.list_table.setColumnHidden(0, True)
        apply_readable_table(self.list_table)
        self.list_table.itemSelectionChanged.connect(self._on_selected)
        self.selected_summary_label = make_workflow_accent_label(
            "選択中: 未選択。復元/完全削除の前に一覧から対象を選択してください。",
            "info",
        )
        self.selected_summary_label.setProperty("selected_target_summary", True)
        self.detail_label = QLabel("詳細: 未選択")
        self.detail_label.setWordWrap(True)

        self.reload_button = QPushButton("再読込")
        self.restore_button = QPushButton("選択データを復元")
        self.hard_delete_button = QPushButton("選択データを完全削除")
        self.reload_button.clicked.connect(self._reload)
        self.restore_button.clicked.connect(self._restore_selected)
        self.hard_delete_button.clicked.connect(self._hard_delete_selected)

        self.danger_hint_label = make_workflow_accent_label(
            "注意: 完全削除は元に戻せません。"
            "実行前に『選択中』の分類・表示名・公開ID・削除日時・操作者IDを確認してください。",
            "delete",
        )
        self.danger_hint_label.setProperty("danger_operation_hint", True)
        apply_workflow_accent(self.hard_delete_button, "delete")
        self.hard_delete_button.setProperty("danger_operation_button", True)

        form = QFormLayout()
        compact_layout(form, margins=2, spacing=3)
        form.addRow("表示対象", self.entity_selector)
        form.addRow("操作者ID", self.operator_input)

        actions = QHBoxLayout()
        compact_layout(actions, margins=0, spacing=4)
        actions.addWidget(self.reload_button)
        actions.addWidget(self.restore_button)
        actions.addWidget(self.hard_delete_button)

        root = QVBoxLayout(self)
        compact_layout(root, margins=5, spacing=4)
        root.addWidget(PageHeader("削除データ", "復元と完全削除をここに集約します。"))
        root.addLayout(form)
        root.addWidget(self.danger_hint_label)
        root.addWidget(self.selected_summary_label)
        root.addLayout(actions)
        root.addWidget(self.message_label)
        root.addWidget(self.list_table, 1)
        root.addWidget(self.detail_label)

        apply_trash_subtabs(self)
        self._apply_role_guards()
        self._reload()

    def _entity_key(self) -> str:
        return {
            "すべて": "all",
            "All": "all",
            "名前": "name",
            "Name": "name",
            "タイトル": "title",
            "Title": "title",
            "サブタイトル": "subtitle",
            "Subtitle": "subtitle",
            "リンク": "link",
            "Link": "link",
        }.get(self.entity_selector.currentText(), "all")

    def _apply_role_guards(self) -> None:
        enabled = can_run_destructive_actions(self._role_context.role)
        self.restore_button.setEnabled(enabled)
        self.hard_delete_button.setEnabled(enabled)
        tooltip = (
            "このロールでは実行できません"
            if not enabled
            else "削除済みデータを選択してください"
        )
        self.restore_button.setToolTip(tooltip)
        self.hard_delete_button.setToolTip(tooltip)

    def _reload(self) -> None:
        key = self._entity_key()
        self._selected = None
        self.selected_summary_label.setText(
            "選択中: 未選択。復元/完全削除の前に一覧から対象を選択してください。"
        )
        self.detail_label.setText("詳細: 未選択")
        try:
            rows: list[_TrashRow] = []
            if key in {"all", "name"}:
                rows.extend(
                    _row_from_name(row)
                    for row in self._query_service.list_deleted_names(
                        role=self._role_context.role
                    )
                )
            if key in {"all", "title"}:
                rows.extend(
                    _row_from_title(row)
                    for row in self._query_service.list_deleted_titles(
                        role=self._role_context.role
                    )
                )
            if key in {"all", "subtitle"}:
                rows.extend(
                    _row_from_subtitle(row)
                    for row in self._query_service.list_deleted_subtitles(
                        role=self._role_context.role
                    )
                )
            if key in {"all", "link"}:
                rows.extend(
                    _row_from_link(row)
                    for row in self._query_service.list_deleted_links(
                        role=self._role_context.role
                    )
                )
        except Exception as exc:  # noqa: BLE001
            self._trash_rows = []
            self.list_table.setRowCount(0)
            self._set_message(f"一覧取得に失敗しました: {exc}", is_error=True)
            return

        self._trash_rows = sorted(
            rows,
            key=lambda row: (row.deleted_at or "", row.entity_label, row.entity_id),
            reverse=True,
        )
        self._render_rows()
        if self.list_table.rowCount() > 0:
            self.list_table.selectRow(0)
            self._on_selected()
            self._set_message(f"削除済みデータを {self.list_table.rowCount()} 件表示しました")
        else:
            self._set_message("削除済みデータはありません")

    def _render_rows(self) -> None:
        self.list_table.setRowCount(len(self._trash_rows))
        for i, row in enumerate(self._trash_rows):
            self.list_table.setItem(i, 0, QTableWidgetItem(str(row.entity_id)))
            self.list_table.setItem(i, 1, QTableWidgetItem(row.entity_label))
            self.list_table.setItem(i, 2, QTableWidgetItem(short_public_id(row.public_id)))
            self.list_table.setItem(i, 3, QTableWidgetItem(row.display_name))
            self.list_table.setItem(i, 4, QTableWidgetItem(row.title_name))
            self.list_table.setItem(i, 5, QTableWidgetItem(row.subtitle_code))
            self.list_table.setItem(i, 6, QTableWidgetItem(_deleted_at_display(row)))
            self.list_table.setItem(i, 7, QTableWidgetItem(row.detail))

    def _on_selected(self) -> None:
        row_index = self.list_table.currentRow()
        if row_index < 0 or row_index >= len(self._trash_rows):
            self._selected = None
            self.selected_summary_label.setText(
                "選択中: 未選択。復元/完全削除の前に一覧から対象を選択してください。"
            )
            self.detail_label.setText("詳細: 未選択")
            return
        self._selected = self._trash_rows[row_index]
        summary = _selected_summary(self._selected)
        self.selected_summary_label.setText(f"選択中: {summary}")
        self.detail_label.setText(
            f"詳細: {summary} / 削除日時={_deleted_at_display(self._selected)} / "
            f"{self._selected.detail}"
        )

    def _restore_selected(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールでは復元できません", is_error=True)
            return
        operator_id = self._require_operator_id()
        selected = self._require_deleted_selection()
        if operator_id is None or selected is None:
            return
        if not confirm_destructive_action(
            self,
            "復元の確認",
            "次の削除済みデータを復元します。\n"
            f"{_selected_summary(selected)}\n"
            f"削除日時: {_deleted_at_display(selected)}\n"
            f"操作者ID: {operator_id}",
        ):
            self._set_message("復元をキャンセルしました")
            return
        method = {
            "name": "restore_name",
            "title": "restore_title",
            "subtitle": "restore_subtitle",
            "link": "restore_link",
        }[selected.entity_key]
        getattr(self._core_service, method)(
            selected.entity_id,
            operator_id,
            role=self._role_context.role,
        )
        self._set_message(f"復元しました: {_selected_summary(selected)}")
        self._reload()

    def _hard_delete_selected(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールでは完全削除できません", is_error=True)
            return
        operator_id = self._require_operator_id()
        selected = self._require_deleted_selection()
        if operator_id is None or selected is None:
            return
        if not confirm_destructive_action(
            self,
            "完全削除の確認",
            "次の削除済みデータを完全削除します。元に戻せません。\n"
            f"{_selected_summary(selected)}\n"
            f"削除日時: {_deleted_at_display(selected)}\n"
            f"操作者ID: {operator_id}",
        ):
            self._set_message("完全削除をキャンセルしました")
            return
        method = {
            "name": "hard_delete_name",
            "title": "hard_delete_title",
            "subtitle": "hard_delete_subtitle",
            "link": "hard_delete_link",
        }[selected.entity_key]
        getattr(self._core_service, method)(
            selected.entity_id,
            operator_id,
            role=self._role_context.role,
        )
        self._set_message(f"完全削除しました: {_selected_summary(selected)}")
        self._reload()

    def _require_operator_id(self) -> str | None:
        operator_id = self.operator_input.text().strip()
        if not operator_id:
            self._set_message("操作者ID を入力してください", is_error=True)
            return None
        return operator_id

    def _require_deleted_selection(self) -> _TrashRow | None:
        if self._selected is None:
            self._on_selected()
        if self._selected is None:
            self._set_message("対象を選択してください", is_error=True)
            return None
        if self._selected.deleted_at is None:
            self._set_message("active データには実行できません", is_error=True)
            return None
        return self._selected

    def _set_message(self, message: str, *, is_error: bool = False) -> None:
        color = "#b00020" if is_error else "#1b5e20"
        self.message_label.setStyleSheet(f"color: {color};")
        self.message_label.setText(message)


def _selected_summary(row: _TrashRow) -> str:
    return (
        f"{row.entity_label} / 表示名={row.display_name or '-'} / "
        f"内部ID={row.entity_id} / 公開ID={short_public_id(row.public_id)}"
    )


def _deleted_at_display(row: _TrashRow) -> str:
    return format_datetime_display(row.deleted_at, fallback="不明")


def _row_from_name(row: NameDetail) -> _TrashRow:
    return _TrashRow(
        entity_key="name",
        entity_label="名前",
        entity_id=row.id,
        public_id=row.public_id,
        display_name=row.raw_name,
        title_name="",
        subtitle_code="",
        deleted_at=row.deleted_at,
        detail=f"検索用表記={row.normalized_name} / 備考={row.note or ''}",
    )


def _row_from_title(row: TitleDetail) -> _TrashRow:
    return _TrashRow(
        entity_key="title",
        entity_label="タイトル",
        entity_id=row.id,
        public_id=row.public_id,
        display_name=row.title_name,
        title_name=row.title_name,
        subtitle_code="",
        deleted_at=row.deleted_at,
        detail=f"備考={row.note or ''}",
    )


def _row_from_subtitle(row: SubtitleDetail) -> _TrashRow:
    return _TrashRow(
        entity_key="subtitle",
        entity_label="サブタイトル",
        entity_id=row.id,
        public_id=row.public_id,
        display_name=row.subtitle_name,
        title_name=f"title_id={row.title_id}",
        subtitle_code=row.subtitle_code,
        deleted_at=row.deleted_at,
        detail=f"表示順={row.sort_order} / 備考={row.note or ''}",
    )


def _row_from_link(row: RelatedRow) -> _TrashRow:
    return _TrashRow(
        entity_key="link",
        entity_label="リンク",
        entity_id=row.link_id,
        public_id=row.link_public_id,
        display_name=f"name_id={row.name_id}",
        title_name=row.title_name,
        subtitle_code=row.subtitle_code,
        deleted_at=row.link_deleted_at,
        detail=(
            f"subtitle_id={row.subtitle_id} / relation_type={row.relation_type} / "
            f"サブタイトル={row.subtitle_name}"
        ),
    )

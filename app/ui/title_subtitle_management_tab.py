"""Title/Subtitle management tab UI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.application.core_services import SubtitleInput, TitleInput
from app.application.read_models import NameSearchRow, NameTitleLinkRow, SubtitleDetail, TitleDetail
from app.ui.dialogs import confirm_destructive_action
from app.ui.input_defaults import default_operator_id, friendly_error_message, generate_subtitle_code
from app.ui.permissions import can_create_or_update, can_run_destructive_actions
from app.ui.public_id_display import short_public_id
from app.ui.role_context import RoleContext, UserRole
from app.ui.ui_style import compact_layout, set_status_message


class TitleSubtitleWriteService(Protocol):
    def create_title(
        self,
        payload: TitleInput,
        operator_id: str,
        role: UserRole = "admin",
        *,
        name_ids: list[int] | None = None,
    ) -> int: ...

    def update_title(
        self,
        title_id: int,
        payload: TitleInput,
        operator_id: str,
        role: UserRole = "admin",
    ) -> None: ...

    def delete_title(self, title_id: int, operator_id: str, role: UserRole = "admin") -> None: ...

    def restore_title(self, title_id: int, operator_id: str, role: UserRole = "admin") -> None: ...

    def hard_delete_title(self, title_id: int, operator_id: str, role: UserRole = "admin") -> None: ...

    def create_subtitle(self, payload: SubtitleInput, operator_id: str, role: UserRole = "admin") -> int: ...

    def update_subtitle(self, subtitle_id: int, payload: SubtitleInput, operator_id: str, role: UserRole = "admin") -> None: ...

    def delete_subtitle(self, subtitle_id: int, operator_id: str, role: UserRole = "admin") -> None: ...

    def restore_subtitle(self, subtitle_id: int, operator_id: str, role: UserRole = "admin") -> None: ...

    def hard_delete_subtitle(self, subtitle_id: int, operator_id: str, role: UserRole = "admin") -> None: ...


class TitleSubtitleReadService(Protocol):
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

    def list_names_for_title(
        self,
        title_id: int,
        role: UserRole = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[NameTitleLinkRow]: ...

    def list_titles(self, role: UserRole = "admin", *, include_deleted: bool = False) -> list[TitleDetail]: ...

    def list_subtitles(self, title_id: int, role: UserRole = "admin", *, include_deleted: bool = False) -> list[SubtitleDetail]: ...


@dataclass(frozen=True)
class _TitleSelection:
    id: int
    deleted: bool


@dataclass(frozen=True)
class _SubtitleSelection:
    id: int
    deleted: bool


def _call_with_optional_role(function: Any, *args: Any, **kwargs: Any) -> Any:
    try:
        return function(*args, **kwargs)
    except TypeError as exc:
        if "unexpected keyword argument 'role'" not in str(exc):
            raise
        kwargs.pop("role", None)
        return function(*args, **kwargs)


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
        self._name_rows: list[NameSearchRow] = []
        self._selected_title: _TitleSelection | None = None
        self._selected_subtitle: _SubtitleSelection | None = None

        self.operator_input = QLineEdit(default_operator_id())
        self.operator_input.setPlaceholderText("操作者（自動入力）")
        self.title_selector_combo = QComboBox()
        self.title_selector_combo.setToolTip("登録済みタイトルを選択します")
        self.title_name_input = QLineEdit()
        self.title_note_input = QLineEdit()
        self.title_link_name_combo = QComboBox()
        self.title_link_name_combo.setToolTip("タイトル作成時に関連付ける名前を1つだけ選択します")
        self.subtitle_code_input = QLineEdit()
        self.subtitle_code_input.setPlaceholderText("未入力なら自動生成")
        self.subtitle_name_input = QLineEdit()
        self.subtitle_sort_order_input = QLineEdit()
        self.subtitle_sort_order_input.setPlaceholderText("0")
        self.subtitle_note_input = QLineEdit()

        self.message_label = QLabel("")
        self.selected_title_label = QLabel("選択中タイトル: 未選択")
        self.subtitle_hint_label = QLabel("タイトルを選択するとサブタイトル操作が有効になります")
        self.title_link_names_list = QListWidget()
        self.title_link_names_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.title_link_names_list.hide()
        self.linked_names_label = QLabel("関連する名前: なし")

        self.titles_table = QTableWidget(0, 7)
        self.titles_table.setHorizontalHeaderLabels(
            ["内部ID", "公開ID", "タイトル名", "状態", "更新日時", "備考", "関連する名前"]
        )
        self.titles_table.setColumnHidden(0, True)
        self.titles_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.titles_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.titles_table.itemSelectionChanged.connect(self._on_title_selected)
        self.title_selector_combo.currentIndexChanged.connect(self._on_title_combo_changed)

        self.subtitles_table = QTableWidget(0, 10)
        self.subtitles_table.setHorizontalHeaderLabels(
            [
                "内部ID",
                "公開ID",
                "タイトル内部ID",
                "タイトル名",
                "管理番号",
                "サブタイトル名",
                "状態",
                "表示順",
                "更新日時",
                "備考",
            ]
        )
        self.subtitles_table.setColumnHidden(0, True)
        self.subtitles_table.setColumnHidden(2, True)
        self.subtitles_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.subtitles_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.subtitles_table.itemSelectionChanged.connect(self._on_subtitle_selected)

        self.title_refresh_button = QPushButton("再読込")
        self.title_create_button = QPushButton("作成")
        self.title_update_button = QPushButton("更新")
        self.title_delete_button = QPushButton("ゴミ箱に入れる")
        self.title_restore_button = QPushButton("復元")
        self.title_hard_delete_button = QPushButton("完全削除")
        self.title_restore_button.hide()
        self.title_hard_delete_button.hide()
        self.subtitle_refresh_button = QPushButton("再読込")
        self.subtitle_create_button = QPushButton("作成")
        self.subtitle_update_button = QPushButton("更新")
        self.subtitle_delete_button = QPushButton("ゴミ箱に入れる")
        self.subtitle_restore_button = QPushButton("復元")
        self.subtitle_hard_delete_button = QPushButton("完全削除")
        self.subtitle_restore_button.hide()
        self.subtitle_hard_delete_button.hide()

        self.title_refresh_button.clicked.connect(self._refresh_titles)
        self.title_create_button.clicked.connect(self._create_title)
        self.title_update_button.clicked.connect(self._update_title)
        self.title_delete_button.clicked.connect(self._delete_title)
        self.title_restore_button.clicked.connect(self._restore_title)
        self.title_hard_delete_button.clicked.connect(self._hard_delete_title)
        self.subtitle_refresh_button.clicked.connect(self._refresh_subtitles)
        self.subtitle_create_button.clicked.connect(self._create_subtitle)
        self.subtitle_update_button.clicked.connect(self._update_subtitle)
        self.subtitle_delete_button.clicked.connect(self._delete_subtitle)
        self.subtitle_restore_button.clicked.connect(self._restore_subtitle)
        self.subtitle_hard_delete_button.clicked.connect(self._hard_delete_subtitle)

        top_form = QFormLayout()
        compact_layout(top_form, margins=0, spacing=2)
        top_form.addRow("操作者ID", self.operator_input)

        title_form = QFormLayout()
        compact_layout(title_form, margins=0, spacing=2)
        title_form.addRow("タイトル選択", self.title_selector_combo)
        title_form.addRow("タイトル名", self.title_name_input)
        title_form.addRow("備考", self.title_note_input)
        title_form.addRow("関連付ける名前", self.title_link_name_combo)

        subtitle_form = QFormLayout()
        compact_layout(subtitle_form, margins=0, spacing=2)
        subtitle_form.addRow("タイトル選択", self.selected_title_label)
        subtitle_form.addRow("管理番号", self.subtitle_code_input)
        subtitle_form.addRow("サブタイトル名", self.subtitle_name_input)
        subtitle_form.addRow("表示順", self.subtitle_sort_order_input)
        subtitle_form.addRow("備考", self.subtitle_note_input)

        title_actions = QHBoxLayout()
        compact_layout(title_actions, margins=0, spacing=3)
        for button in [
            self.title_refresh_button,
            self.title_create_button,
            self.title_update_button,
            self.title_delete_button,
        ]:
            title_actions.addWidget(button)

        subtitle_actions = QHBoxLayout()
        compact_layout(subtitle_actions, margins=0, spacing=3)
        for button in [
            self.subtitle_refresh_button,
            self.subtitle_create_button,
            self.subtitle_update_button,
            self.subtitle_delete_button,
        ]:
            subtitle_actions.addWidget(button)

        title_panel = QWidget()
        self.title_panel = title_panel
        title_layout = QVBoxLayout(title_panel)
        compact_layout(title_layout, margins=2, spacing=3)
        self.title_panel_label = QLabel("タイトル情報")
        title_layout.addWidget(self.title_panel_label)
        title_layout.addLayout(title_form)
        title_layout.addLayout(title_actions)
        title_layout.addWidget(self.linked_names_label)
        title_layout.addWidget(self.titles_table, 2)

        subtitle_panel = QWidget()
        self.subtitle_panel = subtitle_panel
        subtitle_layout = QVBoxLayout(subtitle_panel)
        compact_layout(subtitle_layout, margins=2, spacing=3)
        self.subtitle_panel_label = QLabel("サブタイトル情報")
        subtitle_layout.addWidget(self.subtitle_panel_label)
        subtitle_layout.addWidget(self.subtitle_hint_label)
        subtitle_layout.addLayout(subtitle_form)
        subtitle_layout.addLayout(subtitle_actions)
        subtitle_layout.addWidget(self.subtitles_table, 2)

        splitter = QSplitter()
        self.splitter = splitter
        splitter.addWidget(title_panel)
        splitter.addWidget(subtitle_panel)
        splitter.setSizes([560, 610])

        root = QVBoxLayout(self)
        compact_layout(root, margins=2, spacing=3)
        root.addLayout(top_form)
        root.addWidget(self.message_label)
        root.addWidget(splitter, 1)

        self._configure_table_columns()
        self._apply_role_guards()
        self._refresh_titles()

    def _apply_role_guards(self) -> None:
        self._update_action_states()

    def _refresh_titles(self, selected_title_id: int | None = None) -> None:
        if selected_title_id is None and self._selected_title is not None:
            selected_title_id = self._selected_title.id
        try:
            self._titles = _call_with_optional_role(
                self._query_service.list_titles,
                role=self._role_context.role,
                include_deleted=True,
            )
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"タイトル一覧取得に失敗しました: {exc}", is_error=True)
            return
        self.titles_table.setRowCount(len(self._titles))
        self.title_selector_combo.blockSignals(True)
        self.title_selector_combo.clear()
        for row_index, row in enumerate(self._titles):
            linked_names = self._linked_names_text(row.id)
            self.titles_table.setItem(row_index, 0, QTableWidgetItem(str(row.id)))
            self.titles_table.setItem(row_index, 1, QTableWidgetItem(short_public_id(row.public_id)))
            self.titles_table.setItem(row_index, 2, QTableWidgetItem(row.title_name))
            self.titles_table.setItem(row_index, 3, QTableWidgetItem("削除済み" if row.deleted_at else "有効"))
            self.titles_table.setItem(row_index, 4, QTableWidgetItem(row.updated_at))
            self.titles_table.setItem(row_index, 5, QTableWidgetItem(row.note or ""))
            self.titles_table.setItem(row_index, 6, QTableWidgetItem(linked_names))
            self.title_selector_combo.addItem(_title_combo_label(row), row.id)
        self.title_selector_combo.blockSignals(False)
        self._selected_title = None
        self._selected_subtitle = None
        self._subtitles = []
        self.subtitles_table.setRowCount(0)
        self._update_selected_title_label()
        self._clear_subtitle_form()
        self._refresh_name_candidates()
        self._update_action_states()
        if not self._titles:
            return
        selected_index = 0
        if selected_title_id is not None:
            for row_index, row in enumerate(self._titles):
                if row.id == selected_title_id:
                    selected_index = row_index
                    break
        self.title_selector_combo.setCurrentIndex(selected_index)
        self.titles_table.selectRow(selected_index)
        self._select_title_by_index(selected_index)

    def _refresh_subtitles(self, selected_subtitle_id: int | None = None) -> None:
        title = self._selected_title
        if title is None:
            self._subtitles = []
            self._selected_subtitle = None
            self.subtitles_table.setRowCount(0)
            self._clear_subtitle_form()
            self._update_action_states()
            return
        try:
            self._subtitles = _call_with_optional_role(
                self._query_service.list_subtitles,
                title.id,
                role=self._role_context.role,
                include_deleted=True,
            )
        except Exception as exc:  # noqa: BLE001
            self._set_message(f"サブタイトル一覧取得に失敗しました: {exc}", is_error=True)
            return
        title_name = self._selected_title_name()
        self.subtitles_table.setRowCount(len(self._subtitles))
        for row_index, row in enumerate(self._subtitles):
            self.subtitles_table.setItem(row_index, 0, QTableWidgetItem(str(row.id)))
            self.subtitles_table.setItem(row_index, 1, QTableWidgetItem(short_public_id(row.public_id)))
            self.subtitles_table.setItem(row_index, 2, QTableWidgetItem(str(row.title_id)))
            self.subtitles_table.setItem(row_index, 3, QTableWidgetItem(title_name))
            self.subtitles_table.setItem(row_index, 4, QTableWidgetItem(row.subtitle_code))
            self.subtitles_table.setItem(row_index, 5, QTableWidgetItem(row.subtitle_name))
            self.subtitles_table.setItem(row_index, 6, QTableWidgetItem("削除済み" if row.deleted_at else "有効"))
            self.subtitles_table.setItem(row_index, 7, QTableWidgetItem(str(row.sort_order)))
            self.subtitles_table.setItem(row_index, 8, QTableWidgetItem(row.updated_at))
            self.subtitles_table.setItem(row_index, 9, QTableWidgetItem(row.note or ""))
        self._selected_subtitle = None
        self._clear_subtitle_form()
        if title.deleted or not self._subtitles:
            self._update_action_states()
            return
        selected_index = 0
        if selected_subtitle_id is not None:
            for row_index, row in enumerate(self._subtitles):
                if row.id == selected_subtitle_id:
                    selected_index = row_index
                    break
        self.subtitles_table.selectRow(selected_index)
        self._select_subtitle_by_index(selected_index)

    def _on_title_combo_changed(self, index: int) -> None:
        if 0 <= index < len(self._titles):
            self.titles_table.selectRow(index)
            self._select_title_by_index(index)

    def _on_title_selected(self) -> None:
        self._select_title_by_index(self.titles_table.currentRow())

    def _select_title_by_index(self, index: int) -> None:
        if index < 0 or index >= len(self._titles):
            self._selected_title = None
            self._selected_subtitle = None
            self._subtitles = []
            self.subtitles_table.setRowCount(0)
            self._update_selected_title_label()
            self._clear_subtitle_form()
            self._update_action_states()
            return
        row = self._titles[index]
        self._selected_title = _TitleSelection(row.id, row.deleted_at is not None)
        self.title_selector_combo.blockSignals(True)
        self.title_selector_combo.setCurrentIndex(index)
        self.title_selector_combo.blockSignals(False)
        self.title_name_input.setText(row.title_name)
        self.title_note_input.setText(row.note or "")
        self._update_selected_title_label(row)
        self._refresh_linked_names(row.id)
        self._refresh_subtitles()

    def _on_subtitle_selected(self) -> None:
        self._select_subtitle_by_index(self.subtitles_table.currentRow())

    def _select_subtitle_by_index(self, index: int) -> None:
        if index < 0 or index >= len(self._subtitles):
            self._selected_subtitle = None
            self._clear_subtitle_form()
            self._update_action_states()
            return
        row = self._subtitles[index]
        self._selected_subtitle = _SubtitleSelection(row.id, row.deleted_at is not None)
        self.subtitle_code_input.setText(row.subtitle_code)
        self.subtitle_name_input.setText(row.subtitle_name)
        self.subtitle_sort_order_input.setText(str(row.sort_order))
        self.subtitle_note_input.setText(row.note or "")
        self._update_action_states()

    def _create_title(self) -> None:
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールではタイトル作成できません", is_error=True)
            return
        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        try:
            self._core_service.create_title(
                self._title_payload(),
                operator_id=operator_id,
                role=self._role_context.role,
                name_ids=self._selected_name_ids_for_create(),
            )
            self._set_message("タイトル作成しました")
            self._refresh_titles()
        except Exception as exc:  # noqa: BLE001
            self._set_message(friendly_error_message("タイトル作成", exc), is_error=True)

    def _update_title(self) -> None:
        selected = self._require_selected_title()
        operator_id = self._require_operator_id()
        if selected is None or operator_id is None:
            return
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールではタイトル更新できません", is_error=True)
            return
        if selected.deleted:
            self._set_message("削除済みタイトルは更新できません", is_error=True)
            return
        try:
            self._core_service.update_title(
                selected.id,
                self._title_payload(),
                operator_id=operator_id,
                role=self._role_context.role,
            )
            self._set_message("タイトル更新しました")
            self._refresh_titles(selected.id)
        except Exception as exc:  # noqa: BLE001
            self._set_message(friendly_error_message("タイトル更新", exc), is_error=True)

    def _create_subtitle(self) -> None:
        selected = self._require_selected_title()
        operator_id = self._require_operator_id()
        if selected is None or operator_id is None:
            return
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールではサブタイトル作成できません", is_error=True)
            return
        if selected.deleted:
            self._set_message("削除済みタイトルにはサブタイトル作成できません", is_error=True)
            return
        try:
            self._core_service.create_subtitle(
                self._subtitle_payload(selected.id),
                operator_id=operator_id,
                role=self._role_context.role,
            )
            self._set_message("サブタイトル作成しました")
            self._refresh_subtitles()
        except Exception as exc:  # noqa: BLE001
            self._set_message(friendly_error_message("サブタイトル作成", exc), is_error=True)

    def _update_subtitle(self) -> None:
        selected_title = self._require_selected_title()
        selected_subtitle = self._require_selected_subtitle()
        operator_id = self._require_operator_id()
        if selected_title is None or selected_subtitle is None or operator_id is None:
            return
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールではサブタイトル更新できません", is_error=True)
            return
        if selected_title.deleted or selected_subtitle.deleted:
            self._set_message("削除済みデータは更新できません", is_error=True)
            return
        try:
            self._core_service.update_subtitle(
                selected_subtitle.id,
                self._subtitle_payload(selected_title.id),
                operator_id=operator_id,
                role=self._role_context.role,
            )
            self._set_message("サブタイトル更新しました")
            self._refresh_subtitles(selected_subtitle.id)
        except Exception as exc:  # noqa: BLE001
            self._set_message(friendly_error_message("サブタイトル更新", exc), is_error=True)

    def _delete_title(self) -> None:
        self._mutate_title("ゴミ箱に入れる", "delete_title", require_deleted=False)

    def _restore_title(self) -> None:
        self._mutate_title("復元", "restore_title", require_deleted=True)

    def _hard_delete_title(self) -> None:
        self._mutate_title("完全削除", "hard_delete_title", require_deleted=True)

    def _delete_subtitle(self) -> None:
        self._mutate_subtitle("ゴミ箱に入れる", "delete_subtitle", require_deleted=False)

    def _restore_subtitle(self) -> None:
        self._mutate_subtitle("復元", "restore_subtitle", require_deleted=True)

    def _hard_delete_subtitle(self) -> None:
        self._mutate_subtitle("完全削除", "hard_delete_subtitle", require_deleted=True)

    def _mutate_title(self, label: str, method_name: str, *, require_deleted: bool) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message(f"このロールではタイトル{label}できません", is_error=True)
            return
        selected = self._require_selected_title()
        operator_id = self._require_operator_id()
        if selected is None or operator_id is None:
            return
        if selected.deleted != require_deleted:
            self._set_message("対象の状態が操作条件に合いません", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            f"{label}の確認",
            f"タイトルID={selected.id} を{label}します。よろしいですか？",
        ):
            return
        getattr(self._core_service, method_name)(selected.id, operator_id=operator_id, role=self._role_context.role)
        self._set_message(f"タイトルを{label}しました")
        self._refresh_titles(None if method_name == "hard_delete_title" else selected.id)

    def _mutate_subtitle(self, label: str, method_name: str, *, require_deleted: bool) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message(f"このロールではサブタイトル{label}できません", is_error=True)
            return
        selected_title = self._require_selected_title()
        selected_subtitle = self._require_selected_subtitle()
        operator_id = self._require_operator_id()
        if selected_title is None or selected_subtitle is None or operator_id is None:
            return
        if selected_title.deleted or selected_subtitle.deleted != require_deleted:
            self._set_message("対象の状態が操作条件に合いません", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            f"{label}の確認",
            f"サブタイトルID={selected_subtitle.id} を{label}します。よろしいですか？",
        ):
            return
        getattr(self._core_service, method_name)(selected_subtitle.id, operator_id=operator_id, role=self._role_context.role)
        self._set_message(f"サブタイトルを{label}しました")
        self._refresh_subtitles(None if method_name == "hard_delete_subtitle" else selected_subtitle.id)

    def _title_payload(self) -> TitleInput:
        return TitleInput(title_name=self.title_name_input.text(), note=self.title_note_input.text() or None)

    def _subtitle_payload(self, title_id: int) -> SubtitleInput:
        sort_order_text = self.subtitle_sort_order_input.text().strip() or "0"
        subtitle_code = self.subtitle_code_input.text().strip() or generate_subtitle_code()
        self.subtitle_code_input.setText(subtitle_code)
        return SubtitleInput(
            title_id=title_id,
            subtitle_code=subtitle_code,
            subtitle_name=self.subtitle_name_input.text(),
            sort_order=int(sort_order_text),
            note=self.subtitle_note_input.text() or None,
        )

    def _refresh_name_candidates(self) -> None:
        try:
            self._name_rows = _call_with_optional_role(
                self._query_service.search_names,
                include_deleted=False,
                role=self._role_context.role,
            )
        except Exception:  # noqa: BLE001
            self._name_rows = []
        self.title_link_names_list.clear()
        self.title_link_name_combo.blockSignals(True)
        self.title_link_name_combo.clear()
        self.title_link_name_combo.addItem("関連付けなし", None)
        for row in self._name_rows:
            label = f"{row.raw_name} / 公開ID={short_public_id(row.public_id)}"
            self.title_link_name_combo.addItem(label, row.id)
            item = QListWidgetItem(label)
            item.setData(0x0100, row.id)
            item.setToolTip(f"内部ID={row.id} / 公開ID={row.public_id or '未採番'}")
            self.title_link_names_list.addItem(item)
        self.title_link_name_combo.blockSignals(False)

    def _selected_name_ids_for_create(self) -> list[int]:
        selected_id = self.title_link_name_combo.currentData()
        if selected_id is None:
            return []
        return [int(selected_id)]

    def _refresh_linked_names(self, title_id: int) -> None:
        text = self._linked_names_text(title_id)
        self.linked_names_label.setText(f"関連する名前: {text or 'なし'}")

    def _linked_names_text(self, title_id: int) -> str:
        try:
            rows = _call_with_optional_role(
                self._query_service.list_names_for_title,
                title_id,
                role=self._role_context.role,
                include_deleted=False,
            )
        except Exception:  # noqa: BLE001
            return "取得失敗"
        if not rows:
            return ""
        return ", ".join(row.raw_name for row in rows)

    def _selected_title_name(self) -> str:
        if self._selected_title is None:
            return ""
        for row in self._titles:
            if row.id == self._selected_title.id:
                return row.title_name
        return ""

    def _require_operator_id(self) -> str | None:
        operator_id = self.operator_input.text().strip()
        if not operator_id:
            self._set_message("操作者ID を入力してください", is_error=True)
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
        set_status_message(
            self.message_label,
            message,
            level="error" if is_error else "success",
        )

    def _clear_subtitle_form(self) -> None:
        self.subtitle_code_input.clear()
        self.subtitle_name_input.clear()
        self.subtitle_sort_order_input.clear()
        self.subtitle_note_input.clear()

    def _update_selected_title_label(self, title: TitleDetail | None = None) -> None:
        if title is None:
            self.selected_title_label.setText("選択中タイトル: 未選択")
            return
        status = "削除済み" if title.deleted_at else "有効"
        self.selected_title_label.setText(
            f"公開ID={short_public_id(title.public_id)} / {title.title_name} ({status})"
        )

    def _update_action_states(self) -> None:
        role = self._role_context.role
        can_write = can_create_or_update(role)
        can_destructive = can_run_destructive_actions(role)
        has_title = self._selected_title is not None
        title_deleted = bool(self._selected_title and self._selected_title.deleted)
        has_subtitle = self._selected_subtitle is not None
        subtitle_deleted = bool(self._selected_subtitle and self._selected_subtitle.deleted)

        readonly = "viewerは参照専用です。追加・更新系の入力はできません"
        self.operator_input.setEnabled(can_write or can_destructive)
        for widget in (self.title_name_input, self.title_note_input, self.title_link_name_combo, self.title_link_names_list):
            widget.setEnabled(can_write)
            widget.setToolTip("入力できます" if can_write else readonly)
        subtitle_edit_enabled = can_write and has_title and not title_deleted
        for widget in (
            self.subtitle_code_input,
            self.subtitle_name_input,
            self.subtitle_sort_order_input,
            self.subtitle_note_input,
        ):
            widget.setEnabled(subtitle_edit_enabled)
            widget.setToolTip("入力できます" if subtitle_edit_enabled else readonly)

        self.title_create_button.setEnabled(can_write)
        self.title_update_button.setEnabled(can_write and has_title and not title_deleted)
        self.title_delete_button.setEnabled(can_destructive and has_title and not title_deleted)
        self.title_restore_button.setEnabled(False)
        self.title_hard_delete_button.setEnabled(False)
        self.subtitle_refresh_button.setEnabled(has_title)
        self.subtitle_create_button.setEnabled(can_write and has_title and not title_deleted)
        self.subtitle_update_button.setEnabled(can_write and has_title and has_subtitle and not title_deleted and not subtitle_deleted)
        self.subtitle_delete_button.setEnabled(can_destructive and has_title and has_subtitle and not title_deleted and not subtitle_deleted)
        self.subtitle_restore_button.setEnabled(False)
        self.subtitle_hard_delete_button.setEnabled(False)
        if not has_title:
            self.subtitle_hint_label.setText("タイトルを選択してください")
        elif title_deleted:
            self.subtitle_hint_label.setText("削除済みタイトルが選択されています（サブタイトル操作は無効）")
        else:
            self.subtitle_hint_label.setText("選択中タイトル配下のサブタイトルを操作できます")
        if role == "viewer":
            self._set_message("viewerはタイトル/サブタイトルの追加・更新・削除を実行できません", is_error=True)

    def _configure_table_columns(self) -> None:
        self.titles_table.setColumnWidth(1, 82)
        self.titles_table.setColumnWidth(2, 150)
        self.titles_table.setColumnWidth(3, 58)
        self.titles_table.setColumnWidth(4, 135)
        self.titles_table.setColumnWidth(5, 105)
        self.titles_table.setColumnWidth(6, 155)
        self.subtitles_table.setColumnWidth(1, 82)
        self.subtitles_table.setColumnWidth(3, 125)
        self.subtitles_table.setColumnWidth(4, 90)
        self.subtitles_table.setColumnWidth(5, 145)
        self.subtitles_table.setColumnWidth(6, 58)
        self.subtitles_table.setColumnWidth(7, 60)
        self.subtitles_table.setColumnWidth(8, 135)
        self.subtitles_table.setColumnWidth(9, 105)


def _title_combo_label(row: TitleDetail) -> str:
    status = "削除済み" if row.deleted_at else "有効"
    return f"{row.title_name} / 公開ID={short_public_id(row.public_id)} / {status}"

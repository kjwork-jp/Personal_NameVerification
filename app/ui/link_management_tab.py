"""Name ↔ Subtitle relationship management tab UI."""

from __future__ import annotations

from typing import Any

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

from app.ui.dialogs import confirm_destructive_action
from app.ui.permissions import can_link, can_unlink
from app.ui.public_id_display import short_public_id
from app.ui.relation_types import RELATION_TYPE_OPTIONS
from app.ui.role_context import RoleContext
from app.ui.ui_style import PageHeader


class LinkManagementTab(QWidget):
    """UI for managing relationships between names and subtitles."""

    def __init__(
        self,
        core_service: Any,
        query_service: Any,
        role_context: RoleContext | None = None,
    ) -> None:
        super().__init__()
        self._core_service = core_service
        self._query_service = query_service
        self._role_context = role_context or RoleContext.admin()
        self._names: list[Any] = []
        self._titles: list[Any] = []
        self._subtitles: list[Any] = []
        self._links: list[Any] = []

        self.operator_input = QLineEdit()
        self.operator_input.setPlaceholderText("操作者名または運用担当者ID")
        self.operator_input.setToolTip("変更履歴に記録する操作者を入力します")
        self.relation_type_combo = QComboBox()
        self.relation_type_combo.addItem("-- 関連の種類を選択 --", "")
        for option in RELATION_TYPE_OPTIONS:
            self.relation_type_combo.addItem(_relation_label(option.label), option.value)
        self.relation_type_combo.setToolTip("名前とサブタイトルの関係を選択してください")
        self.relation_type_combo.currentIndexChanged.connect(self._on_relation_type_changed)
        self.custom_relation_type_input = QLineEdit()
        self.custom_relation_type_input.setPlaceholderText("補足説明（任意）")
        self.custom_relation_type_input.setEnabled(False)
        self.custom_relation_type_input.setToolTip(
            "その他を選択した場合だけ、関係の説明を入力します"
        )
        self.message_label = QLabel("")

        self.names_table = QTableWidget(0, 2)
        self.names_table.setHorizontalHeaderLabels(["内部ID", "名前 / 公開ID"])
        self.names_table.setColumnHidden(0, True)
        self.titles_table = QTableWidget(0, 2)
        self.titles_table.setHorizontalHeaderLabels(["内部ID", "タイトル / 公開ID"])
        self.titles_table.setColumnHidden(0, True)
        self.subtitles_table = QTableWidget(0, 3)
        self.subtitles_table.setHorizontalHeaderLabels(["内部ID", "管理番号", "サブタイトル / 公開ID"])
        self.subtitles_table.setColumnHidden(0, True)
        self.subtitles_table.setColumnHidden(1, True)
        self.links_table = QTableWidget(0, 4)
        self.links_table.setHorizontalHeaderLabels(
            ["内部リンクID", "タイトル / 公開ID", "管理番号", "関連の種類"]
        )
        self.links_table.setColumnHidden(0, True)
        self.links_table.setColumnHidden(2, True)

        self.names_table.itemSelectionChanged.connect(self._refresh_links)
        self.titles_table.itemSelectionChanged.connect(self._refresh_subtitles)
        self.refresh_button = QPushButton("一覧を更新")
        self.link_button = QPushButton("関連付ける")
        self.unlink_button = QPushButton("関連を外す")
        self.refresh_button.clicked.connect(self._refresh_all)
        self.link_button.clicked.connect(self._create_link)
        self.unlink_button.clicked.connect(self._unlink_link)

        form = QFormLayout()
        form.addRow("操作者", self.operator_input)
        form.addRow("関連の種類", self.relation_type_combo)
        form.addRow("補足説明", self.custom_relation_type_input)
        actions = QHBoxLayout()
        actions.addWidget(self.refresh_button)
        actions.addWidget(self.link_button)
        actions.addWidget(self.unlink_button)
        layout = QVBoxLayout(self)
        layout.addWidget(
            PageHeader(
                "関連付け",
                "名前・タイトル・サブタイトルの関連を手動で調整する画面です。"
                "通常はタイトル管理やサブタイトル管理から登録し、例外的な修正だけここで行います。",
            )
        )
        layout.addLayout(form)
        layout.addLayout(actions)
        layout.addWidget(self.message_label)
        layout.addWidget(QLabel("1. 名前を選択"))
        layout.addWidget(self.names_table)
        layout.addWidget(QLabel("2. タイトルを選択"))
        layout.addWidget(self.titles_table)
        layout.addWidget(QLabel("3. サブタイトルを選択"))
        layout.addWidget(self.subtitles_table)
        layout.addWidget(QLabel("現在の関連一覧"))
        layout.addWidget(self.links_table)

        self._apply_role_guards()
        self._refresh_all()

    def _apply_role_guards(self) -> None:
        role = self._role_context.role
        self.link_button.setEnabled(can_link(role))
        self.unlink_button.setEnabled(can_unlink(role))
        self.link_button.setToolTip(
            "このロールでは実行できません"
            if not can_link(role)
            else "操作者・関連の種類・名前・サブタイトルの選択が必要です"
        )
        self.unlink_button.setToolTip(
            "このロールでは実行できません"
            if not can_unlink(role)
            else "解除対象の関連を選択してください"
        )

    def _refresh_all(self) -> None:
        self._names = _call_optional_role(
            self._query_service.search_names,
            include_deleted=False,
            role=self._role_context.role,
        )
        self._titles = _call_optional_role(
            self._query_service.list_titles,
            include_deleted=False,
            role=self._role_context.role,
        )
        self.names_table.setRowCount(len(self._names))
        for row_index, row in enumerate(self._names):
            self.names_table.setItem(row_index, 0, QTableWidgetItem(str(row.id)))
            item = QTableWidgetItem(_name_label(row))
            item.setToolTip(_entity_tooltip("名前", row.id, getattr(row, "public_id", None)))
            self.names_table.setItem(row_index, 1, item)
        self.titles_table.setRowCount(len(self._titles))
        for row_index, row in enumerate(self._titles):
            self.titles_table.setItem(row_index, 0, QTableWidgetItem(str(row.id)))
            item = QTableWidgetItem(_title_label(row))
            item.setToolTip(_entity_tooltip("タイトル", row.id, getattr(row, "public_id", None)))
            self.titles_table.setItem(row_index, 1, item)
        if self._names:
            self.names_table.selectRow(0)
        if self._titles:
            self.titles_table.selectRow(0)
        self._refresh_subtitles()
        self._refresh_links()

    def _selected_name_id(self) -> int | None:
        row_index = self.names_table.currentRow()
        if 0 <= row_index < len(self._names):
            return int(self._names[row_index].id)
        return None

    def _selected_title_id(self) -> int | None:
        row_index = self.titles_table.currentRow()
        if 0 <= row_index < len(self._titles):
            return int(self._titles[row_index].id)
        return None

    def _selected_subtitle_id(self) -> int | None:
        row_index = self.subtitles_table.currentRow()
        if 0 <= row_index < len(self._subtitles):
            return int(self._subtitles[row_index].id)
        return None

    def _selected_link_id(self) -> int | None:
        row_index = self.links_table.currentRow()
        if 0 <= row_index < len(self._links):
            return int(self._links[row_index].link_id)
        return None

    def _refresh_subtitles(self) -> None:
        title_id = self._selected_title_id()
        if title_id is None:
            self._subtitles = []
        else:
            self._subtitles = _call_optional_role(
                self._query_service.list_subtitles,
                title_id,
                include_deleted=False,
                role=self._role_context.role,
            )
        self.subtitles_table.setRowCount(len(self._subtitles))
        for row_index, row in enumerate(self._subtitles):
            self.subtitles_table.setItem(row_index, 0, QTableWidgetItem(str(row.id)))
            self.subtitles_table.setItem(row_index, 1, QTableWidgetItem(row.subtitle_code))
            item = QTableWidgetItem(_subtitle_label(row))
            item.setToolTip(_entity_tooltip("サブタイトル", row.id, getattr(row, "public_id", None)))
            self.subtitles_table.setItem(row_index, 2, item)
        if self._subtitles:
            self.subtitles_table.selectRow(0)

    def _refresh_links(self) -> None:
        name_id = self._selected_name_id()
        if name_id is None:
            self._links = []
        else:
            self._links = _call_optional_role(
                self._query_service.list_related_rows,
                name_id,
                include_deleted=False,
                role=self._role_context.role,
            )
        self.links_table.setRowCount(len(self._links))
        for row_index, row in enumerate(self._links):
            self.links_table.setItem(row_index, 0, QTableWidgetItem(str(row.link_id)))
            title_item = QTableWidgetItem(_related_title_label(row))
            title_item.setToolTip(
                " / ".join(
                    [
                        f"リンク内部ID={row.link_id}",
                        f"リンク公開ID={getattr(row, 'link_public_id', None) or '未採番'}",
                        f"タイトル公開ID={getattr(row, 'title_public_id', None) or '未採番'}",
                        f"サブタイトル公開ID={getattr(row, 'subtitle_public_id', None) or '未採番'}",
                    ]
                )
            )
            self.links_table.setItem(row_index, 1, title_item)
            self.links_table.setItem(row_index, 2, QTableWidgetItem(row.subtitle_code))
            relation_item = QTableWidgetItem(_relation_label(row.relation_type))
            relation_item.setToolTip(f"リンク公開ID={getattr(row, 'link_public_id', None) or '未採番'}")
            self.links_table.setItem(row_index, 3, relation_item)
        if self._links:
            self.links_table.selectRow(0)

    def _on_relation_type_changed(self) -> None:
        is_custom = str(self.relation_type_combo.currentData()) == "other"
        self.custom_relation_type_input.setEnabled(is_custom)
        self.custom_relation_type_input.setToolTip(
            "その他の関係を説明してください" if is_custom else "その他を選択した場合だけ入力できます"
        )
        if not is_custom:
            self.custom_relation_type_input.clear()

    def _create_link(self) -> None:
        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        relation_type = self._selected_relation_type()
        if relation_type is None:
            return
        name_id = self._selected_name_id()
        subtitle_id = self._selected_subtitle_id()
        if name_id is None or subtitle_id is None:
            self._set_message("名前とサブタイトルを選択してください", is_error=True)
            return
        self._core_service.link_name_to_subtitle(
            name_id,
            subtitle_id,
            relation_type=relation_type,
            operator_id=operator_id,
            role=self._role_context.role,
        )
        self._set_message("関連付けを作成しました")
        self._refresh_links()

    def _unlink_link(self) -> None:
        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        link_id = self._selected_link_id()
        if link_id is None:
            self._set_message("外す関連を選択してください", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "関連解除の確認",
            "選択した関連を外します。よろしいですか？",
        ):
            self._set_message("関連解除をキャンセルしました")
            return
        self._core_service.unlink_name_from_subtitle(
            link_id,
            operator_id=operator_id,
            role=self._role_context.role,
        )
        self._set_message("関連を外しました")
        self._refresh_links()

    def _selected_relation_type(self) -> str | None:
        selected_value = str(self.relation_type_combo.currentData())
        if not selected_value:
            self._set_message("関連の種類を選択してください", is_error=True)
            return None
        if selected_value == "other":
            custom_value = self.custom_relation_type_input.text().strip()
            if not custom_value:
                self._set_message("補足説明を入力してください", is_error=True)
                return None
            return custom_value
        return selected_value

    def _require_operator_id(self) -> str | None:
        operator_id = self.operator_input.text().strip()
        if not operator_id:
            self._set_message("操作者を入力してください", is_error=True)
            return None
        return operator_id

    def _set_message(self, message: str, *, is_error: bool = False) -> None:
        color = "#ff8a8a" if is_error else "#7ee787"
        self.message_label.setStyleSheet(f"color: {color};")
        self.message_label.setText(message)


def _name_label(row: Any) -> str:
    return f"{row.raw_name} / 公開ID={short_public_id(getattr(row, 'public_id', None))}"


def _title_label(row: Any) -> str:
    return f"{row.title_name} / 公開ID={short_public_id(getattr(row, 'public_id', None))}"


def _subtitle_label(row: Any) -> str:
    return f"{row.subtitle_name} / 公開ID={short_public_id(getattr(row, 'public_id', None))}"


def _related_title_label(row: Any) -> str:
    return f"{row.title_name} / リンク公開ID={short_public_id(getattr(row, 'link_public_id', None))}"


def _entity_tooltip(label: str, internal_id: int, public_id: str | None) -> str:
    return f"{label}内部ID={internal_id} / {label}公開ID={public_id or '未採番'}"


def _relation_label(value: str) -> str:
    mapping = {
        "primary": "主要",
        "secondary": "補助",
        "alias": "別名",
        "other": "その他",
        "primary（主関連）": "主要",
    }
    return mapping.get(value, value)


def _call_optional_role(function: Any, *args: Any, **kwargs: Any) -> Any:
    try:
        return function(*args, **kwargs)
    except TypeError as exc:
        if "unexpected keyword argument 'role'" not in str(exc):
            raise
        kwargs.pop("role", None)
        return function(*args, **kwargs)

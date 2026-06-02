"""Name ↔ Subtitle relationship management tab UI."""

from __future__ import annotations

from typing import Any, Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.ui.dialogs import confirm_destructive_action
from app.ui.permissions import can_link, can_unlink
from app.ui.public_id_display import public_id_detail
from app.ui.role_context import RoleContext
from app.ui.ui_style import PageHeader, compact_layout


class LinkManagementTab(QWidget):
    """UI for registering and removing name/subtitle relationships."""

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

        self.message_label = QLabel("")

        self.register_name_combo = QComboBox()
        self.register_title_combo = QComboBox()
        self.register_subtitle_combo = QComboBox()
        self.unregister_name_combo = QComboBox()
        self.unregister_link_combo = QComboBox()

        self.refresh_button = QPushButton("再読込")
        self.link_button = QPushButton("関連付けを登録")
        self.unlink_button = QPushButton("関連付けを解除")
        self.refresh_button.clicked.connect(self._refresh_all)
        self.link_button.clicked.connect(self._create_link)
        self.unlink_button.clicked.connect(self._unlink_link)
        self.register_name_combo.currentIndexChanged.connect(self._refresh_registration_subtitles)
        self.register_title_combo.currentIndexChanged.connect(self._refresh_registration_subtitles)
        self.unregister_name_combo.currentIndexChanged.connect(self._refresh_unlink_candidates)

        register_form = QFormLayout()
        compact_layout(register_form, margins=2, spacing=3)
        register_form.addRow("名前", self.register_name_combo)
        register_form.addRow("タイトル", self.register_title_combo)
        register_form.addRow("未関連サブタイトル", self.register_subtitle_combo)

        register_actions = QHBoxLayout()
        compact_layout(register_actions, margins=0, spacing=4)
        register_actions.addStretch(1)
        register_actions.addWidget(self.link_button)

        register_page = QWidget()
        register_layout = QVBoxLayout(register_page)
        compact_layout(register_layout, margins=3, spacing=4)
        register_hint = QLabel(
            "表示名で対象を選びます。公開ID・内部IDは各候補のツールチップで確認できます。"
        )
        register_hint.setWordWrap(True)
        register_layout.addWidget(register_hint)
        register_layout.addLayout(register_form)
        register_layout.addLayout(register_actions)
        register_layout.addStretch(1)

        unregister_form = QFormLayout()
        compact_layout(unregister_form, margins=2, spacing=3)
        unregister_form.addRow("名前", self.unregister_name_combo)
        unregister_form.addRow("既存関連", self.unregister_link_combo)

        unregister_actions = QHBoxLayout()
        compact_layout(unregister_actions, margins=0, spacing=4)
        unregister_actions.addStretch(1)
        unregister_actions.addWidget(self.unlink_button)

        unregister_page = QWidget()
        unregister_layout = QVBoxLayout(unregister_page)
        compact_layout(unregister_layout, margins=3, spacing=4)
        unregister_hint = QLabel(
            "既に関連付いている組み合わせだけを表示します。リンク公開IDはツールチップで確認できます。"
        )
        unregister_hint.setWordWrap(True)
        unregister_layout.addWidget(unregister_hint)
        unregister_layout.addLayout(unregister_form)
        unregister_layout.addLayout(unregister_actions)
        unregister_layout.addStretch(1)

        self.tabs = QTabWidget()
        self.tabs.addTab(register_page, "登録")
        self.tabs.addTab(unregister_page, "解除")

        top_actions = QHBoxLayout()
        compact_layout(top_actions, margins=0, spacing=4)
        top_actions.addStretch(1)
        top_actions.addWidget(self.refresh_button)

        layout = QVBoxLayout(self)
        compact_layout(layout, margins=5, spacing=4)
        layout.addWidget(PageHeader("関連付け", "名前とサブタイトルの登録・解除を分けて操作します。"))
        layout.addLayout(top_actions)
        layout.addWidget(self.message_label)
        layout.addWidget(self.tabs, 1)
        self.setProperty("link_label_normalized", True)

        self._apply_role_guards()
        self._refresh_all()

    def _apply_role_guards(self) -> None:
        role = self._role_context.role
        can_register = can_link(role)
        can_remove = can_unlink(role)
        can_any_write = can_register or can_remove
        disabled = "このロールでは実行できません"

        for widget in (
            self.register_name_combo,
            self.register_title_combo,
            self.register_subtitle_combo,
        ):
            widget.setEnabled(can_register)
            widget.setToolTip(disabled if not can_register else "関連付け対象を選択します")
        for widget in (self.unregister_name_combo, self.unregister_link_combo):
            widget.setEnabled(can_remove)
            widget.setToolTip(disabled if not can_remove else "解除対象を選択します")

        self.link_button.setEnabled(can_register)
        self.unlink_button.setEnabled(can_remove)
        self.tabs.setTabEnabled(0, can_register)
        self.tabs.setTabEnabled(1, can_remove)
        self.link_button.setToolTip(
            disabled if not can_register else "未関連の名前とサブタイトルを関連付けます"
        )
        self.unlink_button.setToolTip(
            disabled if not can_remove else "既存関連を解除します"
        )
        if not can_any_write:
            self._set_message("viewerは関連付けの登録・解除を実行できません", is_error=True)

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
        self._populate_combo(self.register_name_combo, self._names, _name_label, _name_tooltip)
        self._populate_combo(self.unregister_name_combo, self._names, _name_label, _name_tooltip)
        self._populate_combo(self.register_title_combo, self._titles, _title_label, _title_tooltip)
        self._refresh_registration_subtitles()
        self._refresh_unlink_candidates()
        self._apply_role_guards()

    def _refresh_registration_subtitles(self) -> None:
        name_id = self._selected_data(self.register_name_combo)
        title_id = self._selected_data(self.register_title_combo)
        if title_id is None:
            self._subtitles = []
            self.register_subtitle_combo.clear()
            return
        subtitles = _call_optional_role(
            self._query_service.list_subtitles,
            title_id,
            include_deleted=False,
            role=self._role_context.role,
        )
        linked_subtitle_ids: set[int] = set()
        if name_id is not None:
            linked_rows = _call_optional_role(
                self._query_service.list_related_rows,
                name_id,
                include_deleted=False,
                role=self._role_context.role,
            )
            linked_subtitle_ids = {int(row.subtitle_id) for row in linked_rows}
        self._subtitles = [row for row in subtitles if int(row.id) not in linked_subtitle_ids]
        self._populate_combo(
            self.register_subtitle_combo,
            self._subtitles,
            _subtitle_label,
            _subtitle_tooltip,
        )

    def _refresh_unlink_candidates(self) -> None:
        name_id = self._selected_data(self.unregister_name_combo)
        if name_id is None:
            self._links = []
            self.unregister_link_combo.clear()
            return
        self._links = _call_optional_role(
            self._query_service.list_related_rows,
            name_id,
            include_deleted=False,
            role=self._role_context.role,
        )
        self._populate_combo(
            self.unregister_link_combo,
            self._links,
            _link_label,
            _link_tooltip,
            data_attr="link_id",
        )

    def _create_link(self) -> None:
        if not can_link(self._role_context.role):
            self._set_message("このロールでは関連付けを登録できません", is_error=True)
            return
        name_id = self._selected_data(self.register_name_combo)
        subtitle_id = self._selected_data(self.register_subtitle_combo)
        if name_id is None or subtitle_id is None:
            self._set_message("名前と未関連サブタイトルを選択してください", is_error=True)
            return
        self._core_service.link_name_to_subtitle(
            name_id,
            subtitle_id,
            relation_type="primary",
            operator_id=self._role_context.operator_id,
            role=self._role_context.role,
        )
        self._set_message("関連付けを登録しました")
        self._refresh_all()

    def _unlink_link(self) -> None:
        if not can_unlink(self._role_context.role):
            self._set_message("このロールでは関連付けを解除できません", is_error=True)
            return
        link_id = self._selected_data(self.unregister_link_combo)
        if link_id is None:
            self._set_message("解除する既存関連を選択してください", is_error=True)
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
            operator_id=self._role_context.operator_id,
            role=self._role_context.role,
        )
        self._set_message("関連を解除しました")
        self._refresh_all()

    def _populate_combo(
        self,
        combo: QComboBox,
        rows: list[Any],
        label_func: Callable[[Any], str],
        tooltip_func: Callable[[Any], str] | None = None,
        *,
        data_attr: str = "id",
    ) -> None:
        combo.blockSignals(True)
        combo.clear()
        for row in rows:
            combo.addItem(label_func(row), int(getattr(row, data_attr)))
            if tooltip_func is not None:
                combo.setItemData(combo.count() - 1, tooltip_func(row), Qt.ItemDataRole.ToolTipRole)
        combo.blockSignals(False)

    def _selected_data(self, combo: QComboBox) -> int | None:
        if combo.currentIndex() < 0:
            return None
        value = combo.currentData()
        return int(value) if value is not None else None

    def _set_message(self, message: str, *, is_error: bool = False) -> None:
        color = "#ff8a8a" if is_error else "#7ee787"
        self.message_label.setStyleSheet(f"color: {color};")
        self.message_label.setText(message)


def _name_label(row: Any) -> str:
    return str(row.raw_name)


def _title_label(row: Any) -> str:
    return str(row.title_name)


def _subtitle_label(row: Any) -> str:
    return f"{row.subtitle_code} / {row.subtitle_name}"


def _link_label(row: Any) -> str:
    return f"{row.title_name} / {row.subtitle_code} / {row.subtitle_name}"


def _name_tooltip(row: Any) -> str:
    return "\n".join(
        [
            f"名前: {row.raw_name}",
            f"公開ID: {public_id_detail(getattr(row, 'public_id', None))}",
            f"内部ID: {row.id}",
        ]
    )


def _title_tooltip(row: Any) -> str:
    return "\n".join(
        [
            f"タイトル: {row.title_name}",
            f"公開ID: {public_id_detail(getattr(row, 'public_id', None))}",
            f"内部ID: {row.id}",
        ]
    )


def _subtitle_tooltip(row: Any) -> str:
    return "\n".join(
        [
            f"サブタイトル: {row.subtitle_code} / {row.subtitle_name}",
            f"公開ID: {public_id_detail(getattr(row, 'public_id', None))}",
            f"内部ID: {row.id}",
            f"親タイトルID: {row.title_id}",
        ]
    )


def _link_tooltip(row: Any) -> str:
    return "\n".join(
        [
            f"タイトル: {row.title_name}",
            f"サブタイトル: {row.subtitle_code} / {row.subtitle_name}",
            f"リンク公開ID: {public_id_detail(getattr(row, 'link_public_id', None))}",
            f"名前公開ID: {public_id_detail(getattr(row, 'name_public_id', None))}",
            f"タイトル公開ID: {public_id_detail(getattr(row, 'title_public_id', None))}",
            f"サブタイトル公開ID: {public_id_detail(getattr(row, 'subtitle_public_id', None))}",
            f"内部リンクID: {row.link_id}",
        ]
    )


def _call_optional_role(function: Any, *args: Any, **kwargs: Any) -> Any:
    try:
        return function(*args, **kwargs)
    except TypeError as exc:
        if "unexpected keyword argument 'role'" not in str(exc):
            raise
        kwargs.pop("role", None)
        return function(*args, **kwargs)

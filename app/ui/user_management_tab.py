"""Admin-only user management tab."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.application.authorization import ServiceRole
from app.application.user_services import CreateUserInput, UserRecord, UserService
from app.domain.errors import (
    AuthorizationError,
    ConflictError,
    StateTransitionError,
    ValidationError,
)
from app.ui.navigation_guide import OperationGuide, SectionPanel
from app.ui.role_context import RoleContext
from app.ui.ui_style import PageHeader, compact_layout, set_status_message


class UserManagementTab(QWidget):
    """Admin-only tab for local user maintenance."""

    def __init__(self, user_service: UserService, role_context: RoleContext) -> None:
        super().__init__()
        self._user_service = user_service
        self._role_context = role_context

        self.status_label = QLabel()
        set_status_message(
            self.status_label,
            "ユーザー一覧を読み込んでください。",
            level="info",
        )

        self.create_operator_input = QLineEdit()
        self.create_operator_input.setPlaceholderText("例: viewer")
        self.create_operator_input.setToolTip(
            "新規作成するユーザーのログインIDです。例: viewer"
        )
        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText("任意")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.role_combo = QComboBox()
        self.role_combo.addItem("管理者", "admin")
        self.role_combo.addItem("編集者", "editor")
        self.role_combo.addItem("閲覧者", "viewer")

        self.create_button = QPushButton("ユーザー作成")
        self.create_button.clicked.connect(self._create_user)

        self.guide_panel = self._build_guide_panel()
        self.create_group = self._build_create_panel()

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            [
                "操作者ID",
                "表示名",
                "権限",
                "状態",
                "最終ログイン",
                "失敗回数",
                "public_id",
            ]
        )
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.target_operator_input = QLineEdit()
        self.target_operator_input.setPlaceholderText(
            "一覧で行選択すると自動入力。手入力も可"
        )
        self.target_role_combo = QComboBox()
        self.target_role_combo.addItem("管理者", "admin")
        self.target_role_combo.addItem("編集者", "editor")
        self.target_role_combo.addItem("閲覧者", "viewer")
        self.change_role_button = QPushButton("権限変更")
        self.disable_button = QPushButton("無効化")
        self.enable_button = QPushButton("有効化")
        self.refresh_button = QPushButton("再読込")
        self.change_role_button.clicked.connect(self._change_role)
        self.disable_button.clicked.connect(self._disable_user)
        self.enable_button.clicked.connect(self._enable_user)
        self.refresh_button.clicked.connect(self.refresh)
        self.table.itemSelectionChanged.connect(self._copy_selected_operator)

        self.action_group = self._build_action_panel()
        self.list_panel = self._build_list_panel()

        self.sub_tabs = QTabWidget()
        self.sub_tabs.addTab(self.guide_panel, "ガイド")
        self.sub_tabs.addTab(self.create_group, "ユーザー作成")
        self.sub_tabs.addTab(self.list_panel, "ユーザー一覧")
        self.sub_tabs.addTab(self.action_group, "選択ユーザー操作")
        self.sub_tabs.setCurrentIndex(1)

        layout = QVBoxLayout(self)
        compact_layout(layout, margins=6, spacing=5)
        layout.addWidget(
            PageHeader(
                "ユーザー管理",
                "admin専用。ユーザー作成、一覧確認、権限変更、無効化、有効化を行います。",
            ),
            0,
        )
        layout.addWidget(self.status_label, 0)
        layout.addWidget(self.sub_tabs, 1)

        self._apply_permissions()
        self.refresh()

    def _build_guide_panel(self) -> QWidget:
        guide = OperationGuide(
            "操作ガイド",
            [
                "新規ユーザーは『ユーザー作成』サブタブで操作者ID・初期パスワード・権限を入力して作成します。",
                "既存ユーザーを確認する場合は『ユーザー一覧』サブタブを使います。一覧行を選ぶと操作対象IDへ反映されます。",
                "権限変更・無効化・有効化は『選択ユーザー操作』サブタブで実行します。",
                "最後の有効な管理者は、降格・無効化できない仕様です。",
                "ユーザー管理はadmin専用です。viewer/editorでは操作できません。",
            ],
        )
        panel = QWidget()
        layout = QVBoxLayout(panel)
        compact_layout(layout, margins=8, spacing=8)
        layout.addWidget(guide)
        layout.addStretch(1)
        return panel

    def _build_create_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        compact_layout(layout, margins=8, spacing=8)
        layout.addWidget(
            QLabel(
                "新規ユーザーを作成します。操作者IDはログインIDとして使います。"
            )
        )
        layout.addWidget(_field_with_label("操作者ID（ログインID）", self.create_operator_input))
        layout.addWidget(_field_with_label("表示名", self.display_name_input))
        layout.addWidget(_field_with_label("初期パスワード", self.password_input))
        layout.addWidget(_field_with_label("権限", self.role_combo))
        layout.addWidget(self.create_button)
        layout.addStretch(1)
        return SectionPanel("ユーザー作成", panel)

    def _build_list_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        compact_layout(layout, margins=8, spacing=6)
        layout.addWidget(
            QLabel(
                "登録済みユーザーの一覧です。行を選択すると『選択ユーザー操作』の対象操作者IDへ自動入力されます。"
            )
        )
        layout.addWidget(self.table, 1)
        return SectionPanel("ユーザー一覧", panel)

    def _build_action_panel(self) -> QWidget:
        action_row = QHBoxLayout()
        compact_layout(action_row)
        action_row.addWidget(QLabel("選択中/対象の操作者ID"))
        action_row.addWidget(self.target_operator_input, 2)
        action_row.addWidget(QLabel("変更後の権限"))
        action_row.addWidget(self.target_role_combo, 1)
        action_row.addWidget(self.change_role_button)
        action_row.addWidget(self.disable_button)
        action_row.addWidget(self.enable_button)
        action_row.addWidget(self.refresh_button)

        panel = QWidget()
        layout = QVBoxLayout(panel)
        compact_layout(layout, margins=8, spacing=8)
        layout.addWidget(
            QLabel(
                "既存ユーザーを変更します。先に『ユーザー一覧』で対象行を選ぶか、対象操作者IDを手入力してください。"
            )
        )
        layout.addLayout(action_row)
        layout.addStretch(1)
        return SectionPanel("選択ユーザーへの操作", panel)

    def refresh(self) -> None:
        if self._role_context.role != "admin":
            set_status_message(
                self.status_label,
                "ユーザー管理はadmin専用です。",
                level="warning",
            )
            return
        users = self._user_service.list_users(include_disabled=True)
        self.table.setRowCount(0)
        for user in users:
            self._append_user_row(user)
        set_status_message(
            self.status_label,
            f"ユーザー一覧を再読込しました。件数: {len(users)}",
            level="success",
        )

    def _append_user_row(self, user: UserRecord) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        status = "無効" if user.disabled_at is not None else "有効"
        values = [
            user.operator_id,
            user.display_name or "",
            user.role,
            status,
            user.last_login_at or "",
            str(user.failed_login_count),
            user.public_id or "",
        ]
        for column, value in enumerate(values):
            self.table.setItem(row, column, QTableWidgetItem(value))

    def _copy_selected_operator(self) -> None:
        selected = self.table.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        item = self.table.item(row, 0)
        if item is not None:
            self.target_operator_input.setText(item.text())

    def _create_user(self) -> None:
        role = self.role_combo.currentData()
        try:
            self._user_service.create_user(
                CreateUserInput(
                    operator_id=self.create_operator_input.text().strip(),
                    display_name=self.display_name_input.text().strip() or None,
                    password=self.password_input.text(),
                    role=_service_role(role),
                ),
                actor_operator_id=self._role_context.operator_id,
                actor_role=self._role_context.role,
            )
        except (AuthorizationError, ConflictError, ValidationError) as exc:
            set_status_message(self.status_label, str(exc), level="error")
            return
        self.create_operator_input.clear()
        self.display_name_input.clear()
        self.password_input.clear()
        self.refresh()
        self.sub_tabs.setCurrentIndex(2)

    def _change_role(self) -> None:
        role = self.target_role_combo.currentData()
        try:
            self._user_service.change_user_role(
                self.target_operator_input.text().strip(),
                _service_role(role),
                actor_operator_id=self._role_context.operator_id,
                actor_role=self._role_context.role,
            )
        except (AuthorizationError, StateTransitionError, ValidationError) as exc:
            set_status_message(self.status_label, str(exc), level="error")
            return
        self.refresh()
        self.sub_tabs.setCurrentIndex(2)

    def _disable_user(self) -> None:
        try:
            self._user_service.disable_user(
                self.target_operator_input.text().strip(),
                actor_operator_id=self._role_context.operator_id,
                actor_role=self._role_context.role,
            )
        except (AuthorizationError, StateTransitionError, ValidationError) as exc:
            set_status_message(self.status_label, str(exc), level="error")
            return
        self.refresh()
        self.sub_tabs.setCurrentIndex(2)

    def _enable_user(self) -> None:
        try:
            self._user_service.enable_user(
                self.target_operator_input.text().strip(),
                actor_operator_id=self._role_context.operator_id,
                actor_role=self._role_context.role,
            )
        except (AuthorizationError, ValidationError) as exc:
            set_status_message(self.status_label, str(exc), level="error")
            return
        self.refresh()
        self.sub_tabs.setCurrentIndex(2)

    def _apply_permissions(self) -> None:
        enabled = self._role_context.role == "admin"
        for widget in (
            self.create_operator_input,
            self.display_name_input,
            self.password_input,
            self.role_combo,
            self.create_button,
            self.target_operator_input,
            self.target_role_combo,
            self.change_role_button,
            self.disable_button,
            self.enable_button,
        ):
            widget.setEnabled(enabled)


def _field_with_label(label_text: str, field: QWidget) -> QWidget:
    container = QWidget()
    layout = QVBoxLayout(container)
    compact_layout(layout, margins=0, spacing=3)
    label = QLabel(label_text)
    label.setWordWrap(False)
    field.setMinimumHeight(28)
    field.setMinimumWidth(420)
    layout.addWidget(label)
    layout.addWidget(field)
    return container


def _service_role(value: object) -> ServiceRole:
    if value in {"viewer", "editor", "admin"}:
        return value  # type: ignore[return-value]
    raise ValidationError("role is invalid")
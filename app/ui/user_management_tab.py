"""Admin-only user management tab."""

from __future__ import annotations

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

        self.operator_input = QLineEdit()
        self.operator_input.setPlaceholderText("例: viewer")
        self.operator_input.setToolTip("ログイン時に入力する操作者IDです。例: viewer")
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

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setVerticalSpacing(6)
        form.addRow("操作者ID（ログインID）", self.operator_input)
        form.addRow("表示名", self.display_name_input)
        form.addRow("初期パスワード", self.password_input)
        form.addRow("権限", self.role_combo)
        create_body = QWidget()
        create_body_layout = QVBoxLayout(create_body)
        compact_layout(create_body_layout, margins=0, spacing=6)
        create_body_layout.addLayout(form)
        create_body_layout.addWidget(self.create_button)
        self.create_group = SectionPanel("ユーザー作成", create_body)

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

        action_body = QWidget()
        action_body_layout = QVBoxLayout(action_body)
        compact_layout(action_body_layout, margins=0, spacing=6)
        action_body_layout.addWidget(
            QLabel(
                "一覧で対象ユーザーの行を選ぶと、対象操作者IDへ自動入力されます。"
                "権限変更は右の『変更後の権限』を選んでから実行します。"
            )
        )
        action_body_layout.addLayout(action_row)
        self.action_group = SectionPanel("選択ユーザーへの操作", action_body)

        layout = QVBoxLayout(self)
        compact_layout(layout, margins=6, spacing=5)
        layout.addWidget(
            PageHeader(
                "ユーザー管理",
                "admin専用。ユーザー作成、権限変更、無効化、有効化を行います。",
            ),
            0,
        )
        layout.addWidget(
            OperationGuide(
                "操作ガイド",
                [
                    "新規ユーザーは上の『ユーザー作成』で操作者ID・初期パスワード・権限を入力して作成します。",
                    "既存ユーザーを変更する場合は、一覧で対象行を選んでから下の『選択ユーザーへの操作』を使います。",
                    "最後の有効な管理者は、降格・無効化できない仕様です。",
                    "実行結果や失敗理由は緑/赤のメッセージ欄に表示されます。",
                ],
            ),
            0,
        )
        layout.addWidget(self.status_label, 0)
        layout.addWidget(self.create_group, 0)
        layout.addWidget(self.table, 1)
        layout.addWidget(self.action_group, 0)

        self._apply_permissions()
        self.refresh()

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
                    operator_id=self.operator_input.text().strip(),
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
        self.operator_input.clear()
        self.display_name_input.clear()
        self.password_input.clear()
        self.refresh()

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

    def _apply_permissions(self) -> None:
        enabled = self._role_context.role == "admin"
        for widget in (
            self.operator_input,
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


def _service_role(value: object) -> ServiceRole:
    if value in {"viewer", "editor", "admin"}:
        return value  # type: ignore[return-value]
    raise ValidationError("role is invalid")
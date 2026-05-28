"""Login dialog for local and Windows authentication."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from app.application.user_services import UserService
from app.application.windows_identity import WindowsIdentityError, current_windows_identity
from app.domain.errors import AuthorizationError, ValidationError
from app.ui.role_context import RoleContext
from app.ui.ui_style import PageHeader, apply_workflow_accent, compact_layout, set_status_message


class LoginDialog(QDialog):
    """Login dialog that supports Windows session auth and local password auth."""

    def __init__(self, user_service: UserService) -> None:
        super().__init__()
        self._user_service = user_service
        self._role_context: RoleContext | None = None
        self.setWindowTitle("ログイン")
        self.setMinimumWidth(420)

        self.message_label = QLabel("認証方式を選択してください。")
        set_status_message(
            self.message_label,
            "Windows認証またはローカル認証でログインします。",
            level="info",
        )

        self.windows_login_button = QPushButton("Windows認証でログイン")
        self.windows_login_button.setToolTip(
            "現在のWindowsログインユーザーでログインします。未登録の場合はviewerで自動登録します。"
        )
        self.windows_login_button.clicked.connect(self._accept_windows_auth)
        apply_workflow_accent(self.windows_login_button, "guide")

        windows_group = QGroupBox("Windows認証")
        windows_layout = QVBoxLayout(windows_group)
        compact_layout(windows_layout, margins=6, spacing=4)
        windows_hint = QLabel(
            "Windowsの現在ユーザーでログインします。日常利用はこちらを優先します。"
        )
        windows_hint.setWordWrap(True)
        windows_layout.addWidget(windows_hint)
        windows_layout.addWidget(self.windows_login_button)

        self.operator_input = QLineEdit()
        self.operator_input.setPlaceholderText("例: admin")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("パスワード")
        self.password_input.returnPressed.connect(self._accept_if_valid)

        form = QFormLayout()
        compact_layout(form, margins=2, spacing=4)
        form.addRow("操作者ID", self.operator_input)
        form.addRow("パスワード", self.password_input)

        self.local_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.local_buttons.button(QDialogButtonBox.StandardButton.Ok).setText("ローカル認証でログイン")
        self.local_buttons.accepted.connect(self._accept_if_valid)

        local_group = QGroupBox("ローカル認証")
        local_layout = QVBoxLayout(local_group)
        compact_layout(local_layout, margins=6, spacing=4)
        local_hint = QLabel("登録済みの操作者IDとパスワードでログインします。")
        local_hint.setWordWrap(True)
        local_layout.addWidget(local_hint)
        local_layout.addLayout(form)
        local_layout.addWidget(self.local_buttons)

        layout = QVBoxLayout(self)
        compact_layout(layout, margins=8, spacing=6)
        layout.addWidget(
            PageHeader(
                "NameVerification にログイン",
                "利用者の権限に応じて、表示・編集・削除系操作の可否を切り替えます。",
            )
        )
        layout.addWidget(self.message_label)
        layout.addWidget(windows_group)
        layout.addWidget(local_group)
        self.setProperty("improved_login_layout", True)

    def role_context(self) -> RoleContext:
        if self._role_context is None:
            raise RuntimeError("login has not been accepted")
        return self._role_context

    def _accept_windows_auth(self) -> None:
        try:
            identity = current_windows_identity()
            user = self._user_service.authenticate_windows_user(identity)
        except (AuthorizationError, ValidationError, WindowsIdentityError) as exc:
            self._show_error(f"Windows認証に失敗しました: {exc}")
            return

        self._role_context = RoleContext(
            role=user.role,
            operator_id=user.operator_id,
            auth_provider="windows",
        )
        self.accept()

    def _accept_if_valid(self) -> None:
        operator_id = self.operator_input.text().strip()
        password = self.password_input.text()
        if not operator_id:
            self._show_error("操作者IDを入力してください。")
            return
        if not password:
            self._show_error("パスワードを入力してください。")
            return
        try:
            user = self._user_service.authenticate_user(operator_id, password)
        except (AuthorizationError, ValidationError):
            self._show_error("操作者IDまたはパスワードが正しくありません。")
            return

        self._role_context = RoleContext(
            role=user.role,
            operator_id=user.operator_id,
            auth_provider="local",
        )
        self.accept()

    def _show_error(self, message: str) -> None:
        set_status_message(self.message_label, message, level="error")

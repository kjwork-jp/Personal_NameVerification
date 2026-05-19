"""Login dialog for local and Windows authentication."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from app.application.user_services import UserService
from app.application.windows_identity import WindowsIdentityError, current_windows_identity
from app.domain.errors import AuthorizationError, ValidationError
from app.ui.role_context import RoleContext


class LoginDialog(QDialog):
    """Login dialog that supports Windows session auth and local password auth."""

    def __init__(self, user_service: UserService) -> None:
        super().__init__()
        self._user_service = user_service
        self._role_context: RoleContext | None = None
        self.setWindowTitle("ログイン")
        self.operator_input = QLineEdit()
        self.operator_input.setPlaceholderText("例: admin")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("パスワード")
        self.message_label = QLabel(
            "Windows認証またはローカル認証を選択してください。"
        )

        self.windows_login_button = QPushButton("Windows認証でログイン")
        self.windows_login_button.setToolTip(
            "現在のWindowsログインユーザーでログインします。未登録の場合はviewerで自動登録します。"
        )
        self.windows_login_button.clicked.connect(self._accept_windows_auth)

        form = QFormLayout()
        form.addRow("操作者ID", self.operator_input)
        form.addRow("パスワード", self.password_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self._accept_if_valid)

        layout = QVBoxLayout(self)
        layout.addWidget(self.message_label)
        layout.addWidget(self.windows_login_button)
        layout.addWidget(QLabel("ローカル認証"))
        layout.addLayout(form)
        layout.addWidget(buttons)

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
        self.message_label.setStyleSheet("color: #ff8a8a;")
        self.message_label.setText(message)

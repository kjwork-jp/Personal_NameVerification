"""Password login dialog for local users."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from app.application.user_services import UserService
from app.domain.errors import AuthorizationError, ValidationError
from app.ui.input_defaults import default_operator_id
from app.ui.role_context import RoleContext


class LoginDialog(QDialog):
    """Local password login dialog.

    The user's role is loaded from the users table after password authentication.
    """

    def __init__(self, user_service: UserService) -> None:
        super().__init__()
        self._user_service = user_service
        self._role_context: RoleContext | None = None
        self.setWindowTitle("ログイン")
        self.operator_input = QLineEdit(default_operator_id())
        self.operator_input.setPlaceholderText("操作者ID")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("パスワード")
        self.message_label = QLabel("操作者IDとパスワードを入力してください。")

        form = QFormLayout()
        form.addRow("操作者ID", self.operator_input)
        form.addRow("パスワード", self.password_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self._accept_if_valid)

        layout = QVBoxLayout(self)
        layout.addWidget(self.message_label)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def role_context(self) -> RoleContext:
        if self._role_context is None:
            raise RuntimeError("login has not been accepted")
        return self._role_context

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
        )
        self.accept()

    def _show_error(self, message: str) -> None:
        self.message_label.setStyleSheet("color: #ff8a8a;")
        self.message_label.setText(message)
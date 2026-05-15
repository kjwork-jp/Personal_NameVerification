"""Initial admin setup dialog for first-run local authentication."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from app.application.user_services import CreateUserInput, UserService
from app.domain.errors import ConflictError, ValidationError


class InitialAdminSetupDialog(QDialog):
    """Create the first admin user when the users table has no active users."""

    def __init__(self, user_service: UserService) -> None:
        super().__init__()
        self._user_service = user_service
        self.setWindowTitle("初回管理者作成")

        self.message_label = QLabel(
            "初回起動のため、最初の管理者ユーザーを作成してください。"
        )
        self.operator_input = QLineEdit()
        self.operator_input.setPlaceholderText("例: admin")
        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText("任意")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_confirmation_input = QLineEdit()
        self.password_confirmation_input.setEchoMode(QLineEdit.EchoMode.Password)

        form = QFormLayout()
        form.addRow("操作者ID", self.operator_input)
        form.addRow("表示名", self.display_name_input)
        form.addRow("パスワード", self.password_input)
        form.addRow("確認", self.password_confirmation_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._accept_if_valid)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.message_label)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _accept_if_valid(self) -> None:
        operator_id = self.operator_input.text().strip()
        display_name = self.display_name_input.text().strip() or None
        password = self.password_input.text()
        confirmation = self.password_confirmation_input.text()

        if not operator_id:
            self._show_error("操作者IDを入力してください。")
            return
        if not password:
            self._show_error("パスワードを入力してください。")
            return
        if password != confirmation:
            self._show_error("パスワードと確認が一致しません。")
            return

        try:
            self._user_service.create_user(
                CreateUserInput(
                    operator_id=operator_id,
                    display_name=display_name,
                    role="admin",
                    password=password,
                ),
                actor_operator_id="initial_setup",
                actor_role="admin",
            )
        except (ConflictError, ValidationError) as exc:
            self._show_error(str(exc))
            return

        self.accept()

    def _show_error(self, message: str) -> None:
        self.message_label.setStyleSheet("color: #ff8a8a;")
        self.message_label.setText(message)

"""Local login dialog for selecting operator and role."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from app.ui.input_defaults import default_operator_id
from app.ui.role_context import RoleContext


class LoginDialog(QDialog):
    """Small local-only login dialog.

    This is not authentication. It records the local operator and role used for
    audit logs and UI permission guards.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ログイン")
        self.operator_input = QLineEdit(default_operator_id())
        self.operator_input.setPlaceholderText("操作者ID")
        self.role_combo = QComboBox()
        self.role_combo.addItem("管理者", "admin")
        self.role_combo.addItem("編集者", "editor")
        self.role_combo.addItem("閲覧者", "viewer")
        self.message_label = QLabel("ローカル利用前提の操作者・権限選択です。")

        form = QFormLayout()
        form.addRow("操作者", self.operator_input)
        form.addRow("権限", self.role_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self._accept_if_valid)

        layout = QVBoxLayout(self)
        layout.addWidget(self.message_label)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def role_context(self) -> RoleContext:
        return RoleContext(
            role=self.role_combo.currentData(),
            operator_id=self.operator_input.text().strip(),
        )

    def _accept_if_valid(self) -> None:
        if not self.operator_input.text().strip():
            self.message_label.setStyleSheet("color: #ff8a8a;")
            self.message_label.setText("操作者IDを入力してください。")
            return
        self.accept()

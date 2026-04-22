"""Shared UI dialogs."""

from __future__ import annotations

from PySide6.QtWidgets import QMessageBox, QWidget


def confirm_destructive_action(parent: QWidget, title: str, body: str) -> bool:
    """Return True when user explicitly confirms a destructive/state-changing action."""
    answer = QMessageBox.question(
        parent,
        title,
        body,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    return answer == QMessageBox.StandardButton.Yes

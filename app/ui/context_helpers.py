"""Helpers for applying RoleContext to local UI tabs."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QLineEdit

from app.ui.role_context import RoleContext


def apply_operator_context(target: Any, role_context: RoleContext) -> None:
    """Apply the login operator to a tab and hide operator input widgets."""

    operator_input = getattr(target, "operator_input", None)
    if isinstance(operator_input, QLineEdit):
        operator_input.setText(role_context.operator_id)
        operator_input.hide()

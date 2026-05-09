"""Helpers for applying RoleContext to local UI tabs."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QFormLayout, QLayout, QLineEdit, QWidget

from app.ui.role_context import RoleContext


def apply_operator_context(target: Any, role_context: RoleContext) -> None:
    """Apply the login operator to a tab and hide operator input widgets."""

    _apply_operator_to_target(target, role_context)
    editor = getattr(target, "editor", None)
    if editor is not None:
        _apply_operator_to_target(editor, role_context)


def _apply_operator_to_target(target: Any, role_context: RoleContext) -> None:
    operator_input = getattr(target, "operator_input", None)
    if isinstance(operator_input, QLineEdit):
        operator_input.setText(role_context.operator_id)
        _hide_form_label_for_widget(target, operator_input)
        operator_input.hide()


def _hide_form_label_for_widget(root: Any, widget: QWidget) -> None:
    if isinstance(root, QWidget) and root.layout() is not None:
        _hide_form_label_in_layout(root.layout(), widget)


def _hide_form_label_in_layout(layout: QLayout, widget: QWidget) -> None:
    if isinstance(layout, QFormLayout):
        label = layout.labelForField(widget)
        if label is not None:
            label.hide()
    for index in range(layout.count()):
        item = layout.itemAt(index)
        if item is None:
            continue
        child_layout = item.layout()
        if child_layout is not None:
            _hide_form_label_in_layout(child_layout, widget)
        child_widget = item.widget()
        if child_widget is not None and child_widget.layout() is not None:
            _hide_form_label_in_layout(child_widget.layout(), widget)

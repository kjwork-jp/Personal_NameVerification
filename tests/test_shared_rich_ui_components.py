"""Regression coverage for shared rich UI component helpers."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication
QLabel = qt_widgets.QLabel
QPushButton = qt_widgets.QPushButton
QTableWidget = qt_widgets.QTableWidget

from app.ui.ui_style import (  # noqa: E402
    apply_readable_table,
    apply_workflow_accent,
    make_workflow_accent_label,
    set_status_message,
)


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_workflow_accent_labels_support_common_semantic_roles() -> None:
    _app()

    for accent in ["info", "guide", "list", "add", "edit", "delete"]:
        label = make_workflow_accent_label(f"{accent} label", accent)
        assert label.property("workflowAccent") == accent
        assert label.wordWrap()
        assert f"{accent} label" in label.text()
        assert "border" in label.styleSheet()


def test_workflow_accent_buttons_and_tables_share_properties() -> None:
    _app()
    button = QPushButton("Run")
    apply_workflow_accent(button, "edit")

    assert button.property("workflowAccent") == "edit"
    assert "QPushButton" in button.styleSheet()

    table = QTableWidget(0, 3)
    apply_readable_table(table)

    assert table.property("readable_table") is True
    assert not table.verticalHeader().isVisible()
    assert table.horizontalHeader().stretchLastSection()


def test_workflow_accent_button_can_switch_semantic_role() -> None:
    _app()
    button = QPushButton("Apply")

    apply_workflow_accent(button, "guide")
    apply_workflow_accent(button, "edit")

    assert button.property("workflowAccent") == "edit"
    assert "QPushButton" in button.styleSheet()


def test_status_message_uses_fallback_info_style_for_unknown_level() -> None:
    _app()
    label = QLabel()

    set_status_message(label, "hello", level="custom")

    assert label.text() == "hello"
    assert label.wordWrap()
    assert "border" in label.styleSheet()

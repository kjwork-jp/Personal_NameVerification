"""Regression tests for account switch top-level widget cleanup."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication
QWidget = qt_widgets.QWidget

from app.pyside6_main import _close_account_switch_widgets  # noqa: E402


class FakeApplication:
    def quit(self) -> None:
        pass


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_account_switch_cleanup_closes_stray_top_level_widgets() -> None:
    _app()
    fake_app = FakeApplication()
    current_window = QWidget()
    stray_window = QWidget()

    try:
        current_window.show()
        stray_window.show()

        assert current_window.isVisible()
        assert stray_window.isVisible()

        _close_account_switch_widgets(fake_app, current_window)

        assert not current_window.isVisible()
        assert not stray_window.isVisible()
    finally:
        stray_window.deleteLater()
        current_window.deleteLater()


def test_account_switch_cleanup_is_safe_without_extra_windows() -> None:
    _app()
    fake_app = FakeApplication()
    current_window = QWidget()

    try:
        current_window.show()

        _close_account_switch_widgets(fake_app, current_window)

        assert not current_window.isVisible()
    finally:
        current_window.deleteLater()

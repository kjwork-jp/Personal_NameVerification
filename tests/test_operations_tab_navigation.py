"""Tests for Operations tab navigation helpers."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication
QLabel = qt_widgets.QLabel

from app.ui.operations_guidance import (  # noqa: E402
    DATA_IO_PAGE_DESCRIPTION,
    DATA_IO_PAGE_TITLE,
)
from app.ui.operations_tab_navigation import _build_guide_page  # noqa: E402
from app.ui.ui_style import PageHeader  # noqa: E402


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_build_guide_page_includes_data_io_page_header() -> None:
    _app()

    page = _build_guide_page("admin")

    headers = page.findChildren(PageHeader)
    assert len(headers) == 1
    assert headers[0].property("data_io_navigation_header") is True
    labels = page.findChildren(QLabel)
    assert any(label.text() == DATA_IO_PAGE_TITLE for label in labels)
    assert any(label.text() == DATA_IO_PAGE_DESCRIPTION for label in labels)
    assert any(label.objectName() == "operationsRoleGuideLabel" for label in labels)

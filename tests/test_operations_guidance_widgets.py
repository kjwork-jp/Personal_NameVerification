"""Tests for Data I/O guidance widget helpers."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication
QLabel = qt_widgets.QLabel

from app.ui.operations_guidance import (  # noqa: E402
    DATA_IO_LOG_DESCRIPTION,
    DATA_IO_PAGE_DESCRIPTION,
    DATA_IO_PAGE_TITLE,
    DATA_IO_RESULT_DESCRIPTION,
)
from app.ui.operations_guidance_widgets import (  # noqa: E402
    is_data_io_guidance_widget,
    make_data_io_log_hint,
    make_data_io_page_header,
    make_data_io_result_hint,
)
from app.ui.ui_style import PageHeader  # noqa: E402


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_make_data_io_page_header_marks_widget() -> None:
    _app()

    header = make_data_io_page_header()

    assert isinstance(header, PageHeader)
    assert header.property("data_io_page_header") is True
    assert is_data_io_guidance_widget(header)
    labels = header.findChildren(QLabel)
    assert any(label.text() == DATA_IO_PAGE_TITLE for label in labels)
    assert any(label.text() == DATA_IO_PAGE_DESCRIPTION for label in labels)


def test_make_data_io_result_hint_marks_widget() -> None:
    _app()

    label = make_data_io_result_hint()

    assert label.text() == DATA_IO_RESULT_DESCRIPTION
    assert label.property("data_io_result_hint") is True
    assert is_data_io_guidance_widget(label)


def test_make_data_io_log_hint_marks_widget() -> None:
    _app()

    label = make_data_io_log_hint()

    assert label.text() == DATA_IO_LOG_DESCRIPTION
    assert label.property("data_io_log_hint") is True
    assert is_data_io_guidance_widget(label)


def test_plain_label_is_not_data_io_guidance_widget() -> None:
    _app()

    assert not is_data_io_guidance_widget(QLabel("plain"))

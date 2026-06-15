"""Tests for Operations tab navigation helpers."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication
QGroupBox = qt_widgets.QGroupBox
QLabel = qt_widgets.QLabel
QTextEdit = qt_widgets.QTextEdit
QVBoxLayout = qt_widgets.QVBoxLayout
QWidget = qt_widgets.QWidget

from app.ui.operations_guidance import (  # noqa: E402
    DATA_IO_GROUP_DESCRIPTIONS,
    DATA_IO_LOG_DESCRIPTION,
    DATA_IO_PAGE_DESCRIPTION,
    DATA_IO_PAGE_TITLE,
    DATA_IO_RESULT_DESCRIPTION,
)
from app.ui.operations_tab_navigation import (  # noqa: E402
    _build_guide_page,
    _insert_result_hint,
    _page_with_group,
)
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


def test_page_with_group_adds_matching_group_description() -> None:
    _app()

    page = _page_with_group(QGroupBox("復元（破壊的操作）"))

    labels = page.findChildren(QLabel)
    assert any(label.text() == DATA_IO_GROUP_DESCRIPTIONS["復元"] for label in labels)
    assert any(label.property("data_io_group_description") is True for label in labels)


def test_page_with_group_adds_operations_log_description() -> None:
    _app()

    page = _page_with_group(QGroupBox("データ入出力 実行ログ"))

    labels = page.findChildren(QLabel)
    assert any(label.text() == DATA_IO_LOG_DESCRIPTION for label in labels)
    assert any(label.property("data_io_group_description") is True for label in labels)


def test_insert_result_hint_before_result_view() -> None:
    _app()
    widget = QWidget()
    layout = QVBoxLayout(widget)
    before = QLabel("before")
    widget.result_view = QTextEdit()  # type: ignore[attr-defined]
    after = QLabel("after")
    layout.addWidget(before)
    layout.addWidget(widget.result_view)  # type: ignore[attr-defined]
    layout.addWidget(after)

    _insert_result_hint(layout, widget)

    labels = widget.findChildren(QLabel)
    assert any(label.text() == DATA_IO_RESULT_DESCRIPTION for label in labels)
    assert layout.itemAt(1).widget().property("data_io_result_hint") is True
    assert layout.itemAt(2).widget() is widget.result_view  # type: ignore[attr-defined]

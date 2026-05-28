"""Reusable guidance widgets for the Data I/O operations screen."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget

from app.ui.operations_guidance import (
    DATA_IO_LOG_DESCRIPTION,
    DATA_IO_PAGE_DESCRIPTION,
    DATA_IO_PAGE_TITLE,
    DATA_IO_RESULT_DESCRIPTION,
)
from app.ui.ui_style import PageHeader, make_workflow_accent_label


def make_data_io_page_header() -> PageHeader:
    """Create the page-level header for the Data I/O screen."""

    header = PageHeader(DATA_IO_PAGE_TITLE, DATA_IO_PAGE_DESCRIPTION)
    header.setProperty("data_io_page_header", True)
    return header


def make_data_io_result_hint() -> QLabel:
    """Create the result-area hint for the Data I/O screen."""

    label = make_workflow_accent_label(DATA_IO_RESULT_DESCRIPTION, "guide")
    label.setProperty("data_io_result_hint", True)
    return label


def make_data_io_log_hint() -> QLabel:
    """Create the operation-log hint for the Data I/O screen."""

    label = make_workflow_accent_label(DATA_IO_LOG_DESCRIPTION, "guide")
    label.setProperty("data_io_log_hint", True)
    return label


def is_data_io_guidance_widget(widget: QWidget) -> bool:
    """Return true for widgets created by this module."""

    return any(
        bool(widget.property(property_name))
        for property_name in (
            "data_io_page_header",
            "data_io_result_hint",
            "data_io_log_hint",
        )
    )

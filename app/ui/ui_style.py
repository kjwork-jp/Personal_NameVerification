"""Shared UI helpers for a friendlier desktop experience."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QLabel,
    QLayout,
    QVBoxLayout,
    QWidget,
)

_STATUS_COLORS = {
    "info": ("#7ee787", "#26382f", "#3d7a55"),
    "success": ("#7ee787", "#26382f", "#3d7a55"),
    "warning": ("#ffd166", "#3b3325", "#8a6d2d"),
    "error": ("#ff8a8a", "#3b292d", "#8a3d45"),
}


def apply_friendly_theme(widget: QWidget) -> None:
    """Apply a compact, softer application-wide theme."""

    widget.setStyleSheet(
        """
        QMainWindow, QWidget {
            background: #20242b;
            color: #f3f6fb;
            font-size: 12px;
        }
        QTabWidget::pane {
            border: 1px solid #3d4654;
            border-radius: 6px;
            top: -1px;
            background: #242a33;
        }
        QTabBar::tab {
            background: #2d3440;
            color: #f3f6fb;
            padding: 5px 10px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }
        QTabBar::tab:selected {
            background: #4f8cff;
            color: #ffffff;
            font-weight: 700;
        }
        QLineEdit, QComboBox, QTextEdit, QTableWidget {
            background: #2f3642;
            border: 1px solid #566173;
            border-radius: 6px;
            padding: 3px;
            selection-background-color: #4f8cff;
        }
        QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
            border: 1px solid #72d6c9;
        }
        QPushButton {
            background: #3f7dff;
            color: #ffffff;
            border: none;
            border-radius: 7px;
            padding: 4px 9px;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #5f95ff;
        }
        QPushButton:disabled {
            background: #414955;
            color: #9aa5b5;
        }
        QGroupBox {
            border: 1px solid #4b5565;
            border-radius: 7px;
            margin-top: 6px;
            padding: 5px;
            background: #252c36;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px;
            color: #72d6c9;
            font-weight: 700;
        }
        QHeaderView::section {
            background: #36404d;
            color: #ffffff;
            padding: 3px;
            border: none;
            font-weight: 700;
        }
        QTableWidget {
            gridline-color: #3d4654;
            alternate-background-color: #2a313b;
        }
        QWidget#PageHeader {
            background: #2b3442;
            border: 1px solid #4f8cff;
            border-radius: 7px;
        }
        QLabel#PageHeaderTitle {
            font-size: 14px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0px;
        }
        QLabel#PageHeaderDescription {
            color: #c8d3e0;
            line-height: 115%;
        }
        """
    )


def compact_layout(layout: QLayout, *, margins: int = 4, spacing: int = 4) -> None:
    """Apply compact margins and spacing to a layout."""

    layout.setContentsMargins(margins, margins, margins, margins)
    layout.setSpacing(spacing)


def set_status_message(label: QLabel, message: str, *, level: str = "info") -> None:
    """Set a framed status message using a shared visual language."""

    text_color, background_color, border_color = _STATUS_COLORS.get(
        level, _STATUS_COLORS["info"]
    )
    label.setText(message)
    label.setWordWrap(True)
    label.setStyleSheet(
        "QLabel {"
        f"color: {text_color};"
        f"background: {background_color};"
        f"border: 1px solid {border_color};"
        "border-radius: 6px;"
        "padding: 4px 6px;"
        "}"
    )


class PageHeader(QWidget):
    """Compact explanatory header shown at the top of each page."""

    def __init__(self, title: str, description: str) -> None:
        super().__init__()
        self.setObjectName("PageHeader")

        title_label = QLabel(title)
        title_label.setObjectName("PageHeaderTitle")

        description_label = QLabel(description)
        description_label.setObjectName("PageHeaderDescription")
        description_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        compact_layout(layout, margins=5, spacing=1)
        layout.addWidget(title_label)
        layout.addWidget(description_label)

"""Shared UI helpers for a friendlier desktop experience."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


def apply_friendly_theme(widget: QWidget) -> None:
    """Apply a softer application-wide theme.

    The current application still uses the platform dark palette, but this style
    adds clearer sections, larger spacing, and warmer accent colors so the UI
    feels less like a raw database administration tool.
    """

    widget.setStyleSheet(
        """
        QMainWindow, QWidget {
            background: #20242b;
            color: #f3f6fb;
            font-size: 13px;
        }
        QTabWidget::pane {
            border: 1px solid #3d4654;
            border-radius: 10px;
            top: -1px;
            background: #242a33;
        }
        QTabBar::tab {
            background: #2d3440;
            color: #f3f6fb;
            padding: 8px 16px;
            margin-right: 4px;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }
        QTabBar::tab:selected {
            background: #4f8cff;
            color: #ffffff;
            font-weight: 700;
        }
        QLineEdit, QComboBox, QTextEdit, QTableWidget {
            background: #2f3642;
            border: 1px solid #566173;
            border-radius: 8px;
            padding: 6px;
            selection-background-color: #4f8cff;
        }
        QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
            border: 1px solid #72d6c9;
        }
        QPushButton {
            background: #3f7dff;
            color: #ffffff;
            border: none;
            border-radius: 10px;
            padding: 7px 14px;
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
            border-radius: 12px;
            margin-top: 14px;
            padding: 12px;
            background: #252c36;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
            color: #72d6c9;
            font-weight: 700;
        }
        QHeaderView::section {
            background: #36404d;
            color: #ffffff;
            padding: 6px;
            border: none;
            font-weight: 700;
        }
        QTableWidget {
            gridline-color: #3d4654;
            alternate-background-color: #2a313b;
        }
        """
    )


class PageHeader(QWidget):
    """Small explanatory header shown at the top of each page."""

    def __init__(self, title: str, description: str) -> None:
        super().__init__()
        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 18px; font-weight: 700; color: #ffffff; margin-bottom: 2px;"
        )
        description_label = QLabel(description)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("color: #c8d3e0; line-height: 140%;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        self.setStyleSheet(
            "background: #2b3442; border: 1px solid #4f8cff; border-radius: 12px;"
        )

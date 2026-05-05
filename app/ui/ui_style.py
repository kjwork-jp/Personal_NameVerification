"""Shared UI helpers for a friendlier desktop experience."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


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
            border-radius: 8px;
            top: -1px;
            background: #242a33;
        }
        QTabBar::tab {
            background: #2d3440;
            color: #f3f6fb;
            padding: 6px 12px;
            margin-right: 3px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        }
        QTabBar::tab:selected {
            background: #4f8cff;
            color: #ffffff;
            font-weight: 700;
        }
        QLineEdit, QComboBox, QTextEdit, QTableWidget {
            background: #2f3642;
            border: 1px solid #566173;
            border-radius: 7px;
            padding: 4px;
            selection-background-color: #4f8cff;
        }
        QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
            border: 1px solid #72d6c9;
        }
        QPushButton {
            background: #3f7dff;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 5px 10px;
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
            border-radius: 9px;
            margin-top: 10px;
            padding: 8px;
            background: #252c36;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: #72d6c9;
            font-weight: 700;
        }
        QHeaderView::section {
            background: #36404d;
            color: #ffffff;
            padding: 4px;
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
            border-radius: 9px;
        }
        QLabel#PageHeaderTitle {
            font-size: 15px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 1px;
        }
        QLabel#PageHeaderDescription {
            color: #c8d3e0;
            line-height: 125%;
        }
        """
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
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)
        layout.addWidget(title_label)
        layout.addWidget(description_label)

"""Shared UI helpers for a friendlier desktop experience."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QCompleter,
    QGroupBox,
    QHeaderView,
    QLabel,
    QLayout,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

_STATUS_COLORS = {
    "info": ("#7ee787", "#26382f", "#3d7a55"),
    "success": ("#7ee787", "#26382f", "#3d7a55"),
    "warning": ("#ffd166", "#3b3325", "#8a6d2d"),
    "error": ("#ff8a8a", "#3b292d", "#8a3d45"),
}

_WORKFLOW_ACCENTS = {
    "info": ("#7ee787", "#26382f", "#3d7a55", "#16a34a"),
    "list": ("#bfdbfe", "#1e3a5f", "#60a5fa", "#2563eb"),
    "add": ("#bbf7d0", "#173b28", "#4ade80", "#16a34a"),
    "edit": ("#ddd6fe", "#2e245c", "#a78bfa", "#7c3aed"),
    "delete": ("#fecaca", "#4a1f25", "#fb7185", "#dc2626"),
    "guide": ("#a5f3fc", "#17394a", "#22d3ee", "#0891b2"),
}


def ensure_positive_application_font(
    app: QApplication,
    *,
    fallback_point_size: int = 9,
) -> None:
    """Normalize application font size to avoid platform fonts with pointSize -1."""

    font = app.font()
    if font.pointSize() > 0:
        return
    font.setPointSize(fallback_point_size)
    app.setFont(font)


def apply_friendly_theme(widget: QWidget) -> None:
    """Apply a compact, softer application-wide theme."""

    widget.setStyleSheet(
        """
        QMainWindow, QWidget {
            background: #20242b;
            color: #f3f6fb;
            font-size: 9pt;
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
            font-size: 10pt;
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


def apply_workflow_accent(widget: QWidget, accent: str) -> None:
    """Apply a shared workflow color accent to labels, groups, and buttons."""

    text_color, background_color, border_color, button_color = _WORKFLOW_ACCENTS[accent]
    widget.setProperty("workflowAccent", accent)
    if isinstance(widget, QLabel):
        widget.setWordWrap(True)
        widget.setStyleSheet(
            "QLabel {"
            f"color: {text_color};"
            f"background: {background_color};"
            f"border: 1px solid {border_color};"
            "border-radius: 6px;"
            "padding: 4px 6px;"
            "font-weight: 600;"
            "}"
        )
        return
    if isinstance(widget, QGroupBox):
        widget.setStyleSheet(
            "QGroupBox {"
            f"border: 1px solid {border_color};"
            "border-radius: 7px;"
            "margin-top: 6px;"
            "padding: 5px;"
            f"background: {background_color};"
            "}"
            "QGroupBox::title {"
            "subcontrol-origin: margin;"
            "left: 8px;"
            "padding: 0 4px;"
            f"color: {text_color};"
            "font-weight: 700;"
            "}"
        )
        return
    if isinstance(widget, QPushButton):
        widget.setStyleSheet(
            "QPushButton {"
            f"background: {button_color};"
            "color: #ffffff;"
            "border: none;"
            "border-radius: 7px;"
            "padding: 4px 9px;"
            "font-weight: 700;"
            "}"
            "QPushButton:hover {"
            f"background: {border_color};"
            "}"
            "QPushButton:disabled {"
            "background: #414955;"
            "color: #9aa5b5;"
            "}"
        )
        return
    widget.setStyleSheet(
        "QWidget {"
        f"background: {background_color};"
        f"border: 1px solid {border_color};"
        "border-radius: 6px;"
        "}"
    )


def make_workflow_accent_label(text: str, accent: str) -> QLabel:
    """Create a standard workflow hint label with a semantic accent."""

    label = QLabel(text)
    label.setObjectName("WorkflowAccentLabel")
    apply_workflow_accent(label, accent)
    return label


def apply_readable_table(table: QTableWidget, *, stretch_last_section: bool = True) -> None:
    """Apply readable defaults to dense data tables."""

    table.setAlternatingRowColors(True)
    table.setWordWrap(False)
    table.setShowGrid(False)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setStretchLastSection(stretch_last_section)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    table.setProperty("readable_table", True)


def make_combo_searchable(combo: QComboBox) -> None:
    """Make a combo box searchable without inserting arbitrary typed values."""

    combo.setEditable(True)
    combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
    combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    completer = combo.completer()
    if completer is None:
        completer = QCompleter(combo.model(), combo)
        combo.setCompleter(completer)
    completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    completer.setFilterMode(Qt.MatchFlag.MatchContains)
    completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)


def apply_searchable_comboboxes(root: QWidget) -> None:
    """Apply searchable behavior to every combo box under root."""

    for combo in root.findChildren(QComboBox):
        make_combo_searchable(combo)


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

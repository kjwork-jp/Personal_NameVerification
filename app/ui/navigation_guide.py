"""Small reusable operation-guide widgets for tab-level navigation."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtWidgets import QFrame, QGroupBox, QLabel, QVBoxLayout, QWidget

from app.ui.ui_style import compact_layout


class OperationGuide(QGroupBox):
    """Compact guide that explains what the user should do on a tab."""

    def __init__(self, title: str, steps: Sequence[str]) -> None:
        super().__init__(title)
        self.setObjectName("OperationGuide")
        layout = QVBoxLayout(self)
        compact_layout(layout, margins=8, spacing=3)
        # QGroupBox title uses the margin area. Keep enough top margin so the
        # first guide line is never hidden by the title text.
        layout.setContentsMargins(8, 20, 8, 8)
        for index, step in enumerate(steps, start=1):
            label = QLabel(f"{index}. {step}")
            label.setWordWrap(True)
            layout.addWidget(label)


class SectionPanel(QFrame):
    """Framed section that avoids QGroupBox title overlap with form rows."""

    def __init__(self, title: str, body: QWidget | None = None) -> None:
        super().__init__()
        self.setObjectName("SectionPanel")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            "QFrame#SectionPanel {"
            "border: 1px solid #4b5565;"
            "border-radius: 7px;"
            "background: #252c36;"
            "}"
            "QLabel#SectionPanelTitle {"
            "color: #72d6c9;"
            "font-weight: 700;"
            "}"
        )
        self.title_label = QLabel(title)
        self.title_label.setObjectName("SectionPanelTitle")
        self.body_layout = QVBoxLayout()
        compact_layout(self.body_layout, margins=0, spacing=5)

        layout = QVBoxLayout(self)
        compact_layout(layout, margins=8, spacing=6)
        layout.addWidget(self.title_label)
        layout.addLayout(self.body_layout)
        if body is not None:
            self.body_layout.addWidget(body)

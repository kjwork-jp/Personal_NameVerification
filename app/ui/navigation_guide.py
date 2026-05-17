"""Small reusable operation-guide widgets for tab-level navigation."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout

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

"""Guided wrapper for the Data I/O operations tab."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QVBoxLayout

from app.ui.operations_guidance_widgets import make_data_io_page_header
from app.ui.operations_tab import OperationsTab


class GuidedOperationsTab(OperationsTab):
    """OperationsTab with a page-level guidance header."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._insert_guidance_header()

    def _insert_guidance_header(self) -> None:
        root = self.layout()
        if not isinstance(root, QVBoxLayout):
            return
        header = make_data_io_page_header()
        root.insertWidget(0, header)
        self.setProperty("data_io_guided_layout", True)

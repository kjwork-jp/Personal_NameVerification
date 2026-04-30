"""Audit log UI hotfix."""
from __future__ import annotations
from typing import Any


def apply() -> None:
    from app.ui import audit_log_tab as m
    old = m.AuditLogTab._reload

    def _reload(self: Any) -> None:
        old(self)
        if getattr(self, "_rows", None):
            if self.logs_table.currentRow() < 0:
                self.logs_table.selectRow(0)
            self._on_selected()

    m.AuditLogTab._reload = _reload

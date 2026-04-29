"""Small Operations log viewer filter hotfix."""
from __future__ import annotations
import re
from typing import Any


def apply() -> None:
    from app.ui import operations_tab as m
    m.OperationsTab._filter_log_events = _filter
    m.OperationsTab._sort_log_events = _sort
    m.OperationsTab._sync_action_filter_options = _actions


def _text(event: object) -> str:
    keys = ("timestamp", "action", "role", "status", "message", "source")
    return "\n".join(str(getattr(event, key, "") or "") for key in keys)


def _filter(self: Any, events: list[object]) -> tuple[list[object], str | None]:
    status = self.log_status_filter.currentText()
    action = self.log_action_filter.currentText()
    query = self.log_message_search_input.text().strip()
    results = [e for e in events if (status == "all" or getattr(e, "status", "") == status) and (action == "all" or getattr(e, "action", "") == action)]
    if not query:
        return results, None
    if self.log_regex_checkbox.isChecked():
        flags = 0
        if self.log_regex_ignore_case_checkbox.isChecked():
            flags |= re.IGNORECASE
        if self.log_regex_multiline_checkbox.isChecked():
            flags |= re.MULTILINE
        if self.log_regex_dotall_checkbox.isChecked():
            flags |= re.DOTALL
        try:
            pattern = re.compile(query, flags)
        except re.error as exc:
            return [], str(exc)
        return [e for e in results if pattern.search(_text(e))], None
    q = query.lower()
    return [e for e in results if q in _text(e).lower()], None


def _sort(self: Any, events: list[object]) -> list[object]:
    return sorted(events, key=lambda e: str(getattr(e, "timestamp", "")), reverse=self.log_sort_order.currentText() != "古い順")


def _actions(self: Any, events: list[object]) -> None:
    current = self.log_action_filter.currentText() or "all"
    values = ["all"]
    for event in events:
        action = str(getattr(event, "action", "") or "")
        if action and action not in values:
            values.append(action)
    self.log_action_filter.blockSignals(True)
    self.log_action_filter.clear()
    self.log_action_filter.addItems(values)
    if current in values:
        self.log_action_filter.setCurrentText(current)
    self.log_action_filter.blockSignals(False)

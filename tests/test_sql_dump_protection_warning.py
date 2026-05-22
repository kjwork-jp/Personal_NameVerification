"""Tests for SQL dump protection warning."""

from __future__ import annotations

from typing import Any

from app.ui.sql_dump_protection_warning import (
    SQL_DUMP_PROTECTION_WARNING,
    apply_sql_dump_protection_warning,
)


class _FakeButton:
    def __init__(self) -> None:
        self.tooltip = ""

    def setToolTip(self, value: str) -> None:  # noqa: N802
        self.tooltip = value


class _FakeOperationsTab:
    def __init__(self) -> None:
        self.export_sql_dump_button = _FakeButton()
        self.sql_dump_path_input = _FakeButton()
        self.messages: list[tuple[str, bool]] = []
        self.export_called = False

    def _set_message(self, message: str, *, is_error: bool = False) -> None:
        self.messages.append((message, is_error))

    def _run_export_sql_dump(self) -> None:
        self.export_called = True


def test_sql_dump_warning_sets_tooltips() -> None:
    tab = _FakeOperationsTab()

    apply_sql_dump_protection_warning(tab)

    assert tab.export_sql_dump_button.tooltip == SQL_DUMP_PROTECTION_WARNING
    assert tab.sql_dump_path_input.tooltip == SQL_DUMP_PROTECTION_WARNING
    assert "password_hash" in tab.export_sql_dump_button.tooltip


def test_sql_dump_warning_is_shown_before_export() -> None:
    tab = _FakeOperationsTab()
    apply_sql_dump_protection_warning(tab)

    tab._run_export_sql_dump()

    assert tab.export_called
    assert tab.messages == [(SQL_DUMP_PROTECTION_WARNING, False)]


def test_sql_dump_warning_application_is_idempotent() -> None:
    tab: Any = _FakeOperationsTab()
    apply_sql_dump_protection_warning(tab)
    first_wrapped = tab._run_export_sql_dump

    apply_sql_dump_protection_warning(tab)

    assert tab._run_export_sql_dump is first_wrapped

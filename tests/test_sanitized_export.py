"""Tests for sanitized sharing-oriented JSON export."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.application.export_backup_services import ExportBackupService
from app.infrastructure.export_backup import export_sanitized_tables_to_json
from app.ui.sanitized_export_ui import SANITIZED_EXPORT_TOOLTIP, apply_sanitized_export_ui


class _FakeButton:
    def __init__(self, text: str = "") -> None:
        self.text = text
        self.tooltip = ""
        self.minimum_height = 0
        self.parent = None
        self.clicked = _FakeSignal()

    def setToolTip(self, value: str) -> None:  # noqa: N802
        self.tooltip = value

    def setMinimumHeight(self, value: int) -> None:  # noqa: N802
        self.minimum_height = value

    def parentWidget(self) -> None:  # noqa: N802
        return None


class _FakeSignal:
    def __init__(self) -> None:
        self.callbacks: list[object] = []

    def connect(self, callback: object) -> None:
        self.callbacks.append(callback)


class _FakeLineEdit:
    def __init__(self, text: str) -> None:
        self._text = text

    def text(self) -> str:
        return self._text


class _FakeLayout:
    def __init__(self) -> None:
        self.widgets: list[object] = []

    def addWidget(self, widget: object) -> None:  # noqa: N802
        self.widgets.append(widget)


class _FakeExportService:
    def __init__(self) -> None:
        self.called_with: tuple[Path, str] | None = None

    def export_sanitized_json(self, output_path: Path, role: str = "admin") -> Path:
        self.called_with = (output_path, role)
        return output_path


class _FakeOperationsTab:
    def __init__(self, output_path: str = "sanitized.json") -> None:
        self.export_json_button = _FakeButton("JSON出力")
        self.json_export_path_input = _FakeLineEdit(output_path)
        self._export_backup_service = _FakeExportService()
        self._role = "editor"
        self._cancel_requested = False
        self.messages: list[tuple[str, bool]] = []
        self.operations: list[dict[str, str | None]] = []
        self.recent_paths: list[tuple[str, str]] = []
        self.started_actions: list[str] = []
        self._layout = _FakeLayout()

    def layout(self) -> _FakeLayout:
        return self._layout

    def _ensure_not_busy(self) -> bool:
        return True

    def _require_text(self, line_edit: _FakeLineEdit, label: str) -> str | None:
        value = line_edit.text().strip()
        if value:
            return value
        self._set_message(f"{label} は必須です", is_error=True)
        return None

    def _start_async_operation(
        self,
        action: str,
        label: str,
        work: object,
        on_success: object,
        on_error: object,
    ) -> None:
        self.started_actions.append(action)
        try:
            result = work()
        except Exception as exc:  # pragma: no cover - defensive fake support
            on_error(exc)
        else:
            on_success(result)

    def _push_recent_path(self, field_key: str, value: str) -> None:
        self.recent_paths.append((field_key, value))

    def _set_message(self, message: str, *, is_error: bool = False) -> None:
        self.messages.append((message, is_error))

    def _record_operation(
        self,
        action: str,
        status: str,
        message: str,
        *,
        path: str | None = None,
        path2: str | None = None,
    ) -> None:
        self.operations.append(
            {
                "action": action,
                "status": status,
                "message": message,
                "path": path,
                "path2": path2,
            }
        )


def _make_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE names (id INTEGER PRIMARY KEY, display_name TEXT);
        CREATE TABLE titles (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE subtitles (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE name_subtitle_links (
            id INTEGER PRIMARY KEY,
            name_id INTEGER,
            subtitle_id INTEGER
        );
        CREATE TABLE name_title_links (id INTEGER PRIMARY KEY, name_id INTEGER, title_id INTEGER);
        CREATE TABLE change_logs (id INTEGER PRIMARY KEY, message TEXT);
        CREATE TABLE users (id INTEGER PRIMARY KEY, operator_id TEXT, password_hash TEXT);
        CREATE TABLE user_audit_logs (id INTEGER PRIMARY KEY, action TEXT);
        CREATE TABLE app_settings (key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE schema_migrations (version TEXT PRIMARY KEY);
        INSERT INTO names (display_name) VALUES ('Alice');
        INSERT INTO users (operator_id, password_hash) VALUES ('admin', 'secret-hash');
        INSERT INTO user_audit_logs (action) VALUES ('login');
        INSERT INTO app_settings (key, value) VALUES ('theme', 'dark');
        INSERT INTO schema_migrations (version) VALUES ('001');
        """
    )
    return connection


def test_sanitized_json_export_uses_allowlisted_application_tables(tmp_path: Path) -> None:
    connection = _make_connection()
    output_path = tmp_path / "sharing.json"

    export_sanitized_tables_to_json(connection, output_path)

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert set(payload) == {
        "names",
        "titles",
        "subtitles",
        "name_subtitle_links",
        "name_title_links",
        "change_logs",
    }
    assert payload["names"][0]["display_name"] == "Alice"
    assert "users" not in payload
    assert "user_audit_logs" not in payload
    assert "app_settings" not in payload
    assert "schema_migrations" not in payload
    assert "secret-hash" not in output_path.read_text(encoding="utf-8")


def test_export_backup_service_exposes_sanitized_json(tmp_path: Path) -> None:
    connection = _make_connection()
    output_path = tmp_path / "sharing.json"

    result = ExportBackupService(connection).export_sanitized_json(output_path, role="editor")

    assert result == output_path.resolve()
    payload = json.loads(result.read_text(encoding="utf-8"))
    assert "names" in payload
    assert "users" not in payload


def test_sanitized_export_ui_adds_button_and_runs_export() -> None:
    tab: Any = _FakeOperationsTab("sharing.json")

    apply_sanitized_export_ui(tab)
    tab._run_export_sanitized_json()

    assert tab.export_sanitized_json_button.toolTip() == SANITIZED_EXPORT_TOOLTIP
    assert tab.started_actions == ["export_sanitized_json"]
    assert tab._export_backup_service.called_with == (Path("sharing.json"), "editor")
    assert tab.recent_paths == [("json_export_file", "sharing.json")]
    assert tab.operations[-1]["action"] == "export_sanitized_json"
    assert tab.operations[-1]["status"] == "success"


def test_sanitized_export_ui_is_idempotent() -> None:
    tab: Any = _FakeOperationsTab("sharing.json")

    apply_sanitized_export_ui(tab)
    first_button = tab.export_sanitized_json_button
    first_runner = tab._run_export_sanitized_json
    apply_sanitized_export_ui(tab)

    assert tab.export_sanitized_json_button is first_button
    assert tab._run_export_sanitized_json is first_runner

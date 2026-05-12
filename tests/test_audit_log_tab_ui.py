"""UI tests for AuditLogTab."""

from __future__ import annotations

import os

import pytest

from app.application.read_models import ChangeLogRow

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_core = pytest.importorskip("PySide6.QtCore", exc_type=ImportError)
qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication
QDateTime = qt_core.QDateTime

from app.ui.audit_log_tab import AuditLogTab  # noqa: E402


class StubQueryService:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def list_change_logs(
        self,
        role: str = "admin",
        *,
        entity_type: str | None = None,
        action: str | None = None,
        operator_id: str | None = None,
        created_from: str | None = None,
        created_to: str | None = None,
        limit: int = 200,
    ) -> list[ChangeLogRow]:
        self.calls.append(
            {
                "role": role,
                "entity_type": entity_type,
                "action": action,
                "operator_id": operator_id,
                "created_from": created_from,
                "created_to": created_to,
                "limit": limit,
            }
        )
        return [
            ChangeLogRow(
                id=1,
                entity_type="names",
                entity_id=10,
                action="update",
                operator_id="op-1",
                before_json='{"raw_name":"A","note":null}',
                after_json='{"raw_name":"B","note":"memo"}',
                created_at="2026-01-01T00:00:00Z",
            )
        ]


class RawJsonQueryService(StubQueryService):
    def list_change_logs(self, **kwargs: object) -> list[ChangeLogRow]:
        _ = kwargs
        return [
            ChangeLogRow(
                id=2,
                entity_type="names",
                entity_id=11,
                action="update",
                operator_id="op-1",
                before_json="not-json",
                after_json="also-not-json",
                created_at="2026-01-01T00:00:00Z",
            )
        ]


class FailingQueryService:
    def list_change_logs(self, **kwargs: object) -> list[ChangeLogRow]:
        _ = kwargs
        raise RuntimeError("db unavailable")


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _datetime(value: str) -> QDateTime:
    return QDateTime.fromString(value, "yyyy-MM-dd HH:mm:ss")


def test_audit_log_tab_reload_with_filters_and_detail() -> None:
    _app()
    query = StubQueryService()
    tab = AuditLogTab(query_service=query)

    tab.entity_type_input.setCurrentText("names")
    tab.action_input.setCurrentText("update")
    tab.operator_id_input.setText("op-1")
    tab.created_from_enabled.setChecked(True)
    tab.created_from_input.setDateTime(_datetime("2026-01-01 00:00:00"))
    tab.created_to_enabled.setChecked(True)
    tab.created_to_input.setDateTime(_datetime("2026-01-31 23:59:59"))
    tab.limit_input.setValue(50)

    tab._reload()

    assert query.calls[-1] == {
        "role": "admin",
        "entity_type": "names",
        "action": "update",
        "operator_id": "op-1",
        "created_from": "2025-12-31T15:00:00Z",
        "created_to": "2026-01-31T14:59:59Z",
        "limit": 50,
    }
    assert tab.logs_table.rowCount() == 1
    assert "raw_name: A" in tab.before_json_view.toPlainText()
    assert "note: null" in tab.before_json_view.toPlainText()
    assert "raw_name: B" in tab.after_json_view.toPlainText()
    assert "note: memo" in tab.after_json_view.toPlainText()
    assert "raw_name: A → B" in tab.diff_view.toPlainText()
    assert "note: null → memo" in tab.diff_view.toPlainText()
    assert tab.before_json_view.isReadOnly()
    assert tab.after_json_view.isReadOnly()
    assert tab.diff_view.isReadOnly()


def test_audit_log_tab_all_filters_are_none_by_default() -> None:
    _app()
    query = StubQueryService()
    tab = AuditLogTab(query_service=query)

    tab._reload()

    assert query.calls[-1]["entity_type"] is None
    assert query.calls[-1]["action"] is None
    assert query.calls[-1]["created_from"] is None
    assert query.calls[-1]["created_to"] is None


def test_audit_log_tab_raw_fallback_for_invalid_json() -> None:
    _app()
    tab = AuditLogTab(query_service=RawJsonQueryService())

    tab._reload()

    assert tab.before_json_view.toPlainText() == "not-json"
    assert tab.after_json_view.toPlainText() == "also-not-json"
    assert "解析できません" in tab.diff_view.toPlainText()


def test_audit_log_tab_limit_is_spinbox() -> None:
    _app()
    tab = AuditLogTab(query_service=StubQueryService())
    tab.limit_input.setValue(0)

    tab._reload()

    assert tab.limit_input.value() == 1


def test_audit_log_tab_query_error_shows_error() -> None:
    _app()
    tab = AuditLogTab(query_service=FailingQueryService())

    tab._reload()

    assert "失敗" in tab.message_label.text()

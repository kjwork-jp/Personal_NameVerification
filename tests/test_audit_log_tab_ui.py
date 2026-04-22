"""UI tests for AuditLogTab."""

from __future__ import annotations

import os

import pytest

from app.application.read_models import ChangeLogRow

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

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
                before_json='{"raw_name":"A"}',
                after_json='{"raw_name":"B"}',
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


def test_audit_log_tab_reload_with_filters_and_detail() -> None:
    _app()
    query = StubQueryService()
    tab = AuditLogTab(query_service=query)

    tab.entity_type_input.setText("names")
    tab.action_input.setText("update")
    tab.operator_id_input.setText("op-1")
    tab.created_from_input.setText("2026-01-01T00:00:00Z")
    tab.created_to_input.setText("2026-01-31T23:59:59Z")
    tab.limit_input.setText("50")

    tab._reload()

    assert query.calls[-1] == {
        "role": "admin",
        "entity_type": "names",
        "action": "update",
        "operator_id": "op-1",
        "created_from": "2026-01-01T00:00:00Z",
        "created_to": "2026-01-31T23:59:59Z",
        "limit": 50,
    }
    assert tab.logs_table.rowCount() == 1
    assert tab.before_json_view.toPlainText() == '{"raw_name":"A"}'
    assert tab.after_json_view.toPlainText() == '{"raw_name":"B"}'
    assert tab.before_json_view.isReadOnly()
    assert tab.after_json_view.isReadOnly()


def test_audit_log_tab_invalid_limit_shows_error() -> None:
    _app()
    tab = AuditLogTab(query_service=StubQueryService())
    tab.limit_input.setText("0")

    tab._reload()

    assert "入力エラー" in tab.message_label.text()


def test_audit_log_tab_query_error_shows_error() -> None:
    _app()
    tab = AuditLogTab(query_service=FailingQueryService())

    tab._reload()

    assert "失敗" in tab.message_label.text()

"""Regression coverage for audit and help summary UI."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.application.read_models import ChangeLogRow

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui.audit_log_tab import AuditLogTab  # noqa: E402
from app.ui.help_settings_tab import HelpSettingsTab  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402


class StubAuditQueryService:
    def list_change_logs(self, **kwargs: object) -> list[ChangeLogRow]:
        self.last_filters = kwargs
        return [
            ChangeLogRow(
                id=1,
                entity_type="subtitles",
                entity_id=11,
                action="update",
                operator_id="op-1",
                before_json='{"subtitle_name":"Before"}',
                after_json='{"subtitle_name":"After"}',
                created_at="2026-06-03T00:00:00Z",
                public_id="audit-public-id-001",
            )
        ]


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_audit_log_tab_shows_filterable_summary_and_diff() -> None:
    _app()
    service = StubAuditQueryService()
    tab = AuditLogTab(service, RoleContext(role="admin", operator_id="op-1"))

    assert tab.entity_type_input.isEditable()
    assert tab.action_input.isEditable()
    assert tab.logs_table.rowCount() == 1
    assert tab.logs_table.horizontalHeaderItem(1).text() == "公開ID"
    assert "操作: update" in tab.detail_summary_label.text()
    assert "データ種類: subtitles" in tab.detail_summary_label.text()
    assert "操作者: op-1" in tab.detail_summary_label.text()
    assert "audit-public-id-001" in tab.detail_summary_label.text()
    assert "Before" in tab.before_json_view.toPlainText()
    assert "After" in tab.after_json_view.toPlainText()
    assert service.last_filters["limit"] == 200


def test_help_settings_tab_surfaces_paths_logs_and_sections(tmp_path: Path) -> None:
    _app()
    db_path = tmp_path / "nameverification.db"
    db_path.write_text("db", encoding="utf-8")
    tab = HelpSettingsTab(
        package_root=tmp_path,
        database_path=db_path,
        change_log_jsonl_path=tmp_path / "logs" / "change_logs.jsonl",
        operations_log_jsonl_path=tmp_path / "logs" / "operations.jsonl",
    )

    assert tab.sections.count() == 4
    assert tab.database_exists_input.text() == "あり"
    assert "nameverification.db" in tab.database_path_input.text()
    assert "operations.jsonl" in tab.operations_log_path_input.text()
    assert tab.sections.tabText(0) == "基本情報"
    assert tab.sections.tabText(3) == "操作メモ"

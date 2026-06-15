"""Regression coverage for data I/O operation log summaries."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui.operations_tab import OperationsTab  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402
from tests.test_operations_tab_ui import (  # noqa: E402
    FakeOperationLogger,
    FakeSettings,
    StubBackupRestoreService,
    StubExportBackupService,
    StubImportService,
)


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_operations_tab_exposes_log_filters_and_current_events() -> None:
    _app()
    logger = FakeOperationLogger()
    logger.events.append(
        {
            "action": "export_json",
            "role": "admin",
            "status": "success",
            "message": "exported",
            "path": "/tmp/export.json",
            "path2": None,
        }
    )
    tab = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="admin", operator_id="op-1"),
        settings=FakeSettings(),
        operation_logger=logger,
    )

    assert tab.export_json_button.isEnabled()
    assert tab.import_json_button.isEnabled()
    assert tab.log_source_selector.currentText() == "現在のログのみ"
    assert tab.log_status_filter.currentText() == "すべて"
    assert tab.log_message_search_input.placeholderText() == "メッセージ検索（部分一致）"
    assert "export_json" in tab.operation_log_view.toPlainText()
    assert "exported" in tab.operation_log_view.toPlainText()

"""UI tests for OperationsTab."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui import operations_tab as operations_tab_module  # noqa: E402
from app.ui.operations_tab import MAX_RECENT_PATHS, OperationsTab  # noqa: E402
from app.ui.operations_workers import ImmediateOperationExecutor  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402


class FakeSettings:
    def __init__(self, seed: dict[str, object] | None = None) -> None:
        self.store: dict[str, object] = seed.copy() if seed else {}

    def value(self, key: str, defaultValue: object | None = None) -> object | None:
        return self.store.get(key, defaultValue)

    def setValue(self, key: str, value: object) -> None:
        self.store[key] = value

    def remove(self, key: str) -> None:
        self.store.pop(key, None)


class FakeOperationLogger:
    def __init__(self) -> None:
        self.events: list[dict[str, str | None]] = []
        self.last_include_archives: bool | None = None

    def append(
        self,
        *,
        action: str,
        role: str,
        status: str,
        message: str,
        path: str | None = None,
        path2: str | None = None,
    ) -> None:
        self.events.append(
            {
                "action": action,
                "role": role,
                "status": status,
                "message": message,
                "path": path,
                "path2": path2,
            }
        )

    def read_latest(
        self, limit: int = 100, *, include_archives: bool = False
    ) -> tuple[list[object], int]:
        self.last_include_archives = include_archives

        class _Event:
            def __init__(self, payload: dict[str, str | None]) -> None:
                self.timestamp = "2026-04-23T00:00:00+00:00"
                self.action = payload.get("action") or ""
                self.role = payload.get("role") or ""
                self.status = payload.get("status") or ""
                self.message = payload.get("message") or ""
                self.path = payload.get("path")
                self.path2 = payload.get("path2")

        data = [_Event(payload) for payload in reversed(self.events[-limit:])]
        return data, 0


class FailingOperationLogger(FakeOperationLogger):
    def append(
        self,
        *,
        action: str,
        role: str,
        status: str,
        message: str,
        path: str | None = None,
        path2: str | None = None,
    ) -> None:
        raise RuntimeError("logger failed")


class StubExportBackupService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def export_csv(self, output_dir: Path, role: str = "admin") -> dict[str, Path]:
        self.calls.append(f"export_csv:{output_dir}:{role}")
        return {"names": output_dir / "names.csv"}

    def export_json(self, output_path: Path, role: str = "admin") -> Path:
        self.calls.append(f"export_json:{output_path}:{role}")
        return output_path

    def export_sql_dump(self, output_path: Path, role: str = "admin") -> Path:
        self.calls.append(f"export_sql_dump:{output_path}:{role}")
        return output_path

    def create_backup(self, db_path: Path, backup_path: Path, role: str = "admin") -> Path:
        self.calls.append(f"create_backup:{db_path}:{backup_path}:{role}")
        return backup_path


class StubBackupRestoreService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def restore_database(
        self, backup_path: Path, target_db_path: Path, role: str = "admin"
    ) -> Path:
        self.calls.append(f"restore:{backup_path}:{target_db_path}:{role}")
        return target_db_path


class StubImportService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def import_csv(self, csv_dir: Path, role: str = "admin") -> dict[str, int]:
        self.calls.append(f"import_csv:{csv_dir}:{role}")
        return {"names": 1}

    def import_json(self, json_path: Path, role: str = "admin") -> dict[str, int]:
        self.calls.append(f"import_json:{json_path}:{role}")
        return {"names": 1}


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class DeferredOperationExecutor:
    def __init__(self) -> None:
        self.pending: tuple[object, object, object, object] | None = None
        self.cancel_requested = False

    def submit(
        self,
        work: object,
        on_success: object,
        on_error: object,
        on_finished: object,
    ) -> None:
        self.pending = (work, on_success, on_error, on_finished)

    def request_cancel(self) -> None:
        self.cancel_requested = True

    def succeed(self, result: object) -> None:
        assert self.pending is not None
        _, on_success, _, on_finished = self.pending
        on_success(result)  # type: ignore[misc]
        on_finished()  # type: ignore[misc]
        self.pending = None


def test_operations_tab_role_guards() -> None:
    _app()

    viewer = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="viewer"),
        operation_executor=ImmediateOperationExecutor(),
    )
    assert not viewer.export_csv_button.isEnabled()
    assert not viewer.create_backup_button.isEnabled()
    assert not viewer.restore_button.isEnabled()
    assert not viewer.import_csv_button.isEnabled()

    editor = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="editor"),
        operation_executor=ImmediateOperationExecutor(),
    )
    assert editor.export_csv_button.isEnabled()
    assert editor.create_backup_button.isEnabled()
    assert not editor.restore_button.isEnabled()
    assert not editor.import_json_button.isEnabled()

    admin = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="admin"),
        operation_executor=ImmediateOperationExecutor(),
    )
    assert admin.export_csv_button.isEnabled()
    assert admin.create_backup_button.isEnabled()
    assert admin.restore_button.isEnabled()
    assert admin.import_json_button.isEnabled()


def test_operations_tab_service_calls_and_result_messages(monkeypatch: pytest.MonkeyPatch) -> None:
    _app()
    monkeypatch.setattr(
        operations_tab_module, "confirm_destructive_action", lambda *args, **kwargs: True
    )
    export_service = StubExportBackupService()
    restore_service = StubBackupRestoreService()
    import_service = StubImportService()

    tab = OperationsTab(
        export_backup_service=export_service,
        backup_restore_service=restore_service,
        import_service=import_service,
        role_context=RoleContext(role="admin"),
        operation_logger=FakeOperationLogger(),
        operation_executor=ImmediateOperationExecutor(),
    )

    tab.csv_export_path_input.setText("/tmp/csv")
    tab._run_export_csv()
    assert any(call.startswith("export_csv:/tmp/csv:admin") for call in export_service.calls)

    tab.restore_backup_path_input.setText("/tmp/backup.sqlite3")
    tab.restore_target_db_path_input.setText("/tmp/target.sqlite3")
    tab._run_restore()
    assert any(
        call.startswith("restore:/tmp/backup.sqlite3:/tmp/target.sqlite3:admin")
        for call in restore_service.calls
    )

    tab.import_json_path_input.setText("/tmp/export.json")
    tab._run_import_json()
    assert any(
        call.startswith("import_json:/tmp/export.json:admin") for call in import_service.calls
    )

    result_text = tab.result_view.toPlainText()
    assert "OK" in result_text
    assert "成功" in result_text


def test_operations_tab_destructive_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    _app()
    monkeypatch.setattr(
        operations_tab_module, "confirm_destructive_action", lambda *args, **kwargs: False
    )
    restore_service = StubBackupRestoreService()
    import_service = StubImportService()

    tab = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=restore_service,
        import_service=import_service,
        role_context=RoleContext(role="admin"),
        operation_logger=FakeOperationLogger(),
        operation_executor=ImmediateOperationExecutor(),
    )

    tab.restore_backup_path_input.setText("/tmp/backup.sqlite3")
    tab.restore_target_db_path_input.setText("/tmp/target.sqlite3")
    tab._run_restore()
    assert not restore_service.calls

    tab.import_csv_dir_input.setText("/tmp/csv")
    tab._run_import_csv()
    assert not import_service.calls

    assert "キャンセル" in tab.result_view.toPlainText()


def test_operations_tab_error_message_display() -> None:
    _app()

    class FailingExportService(StubExportBackupService):
        def export_json(self, output_path: Path, role: str = "admin") -> Path:
            raise RuntimeError("boom")

    tab = OperationsTab(
        export_backup_service=FailingExportService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="admin"),
        operation_logger=FakeOperationLogger(),
        operation_executor=ImmediateOperationExecutor(),
    )

    tab.json_export_path_input.setText("/tmp/export.json")
    tab._run_export_json()

    result_text = tab.result_view.toPlainText()
    assert "ERROR" in result_text
    assert "boom" in result_text


def test_operations_tab_browse_updates_inputs_and_history(monkeypatch: pytest.MonkeyPatch) -> None:
    _app()
    settings = FakeSettings()

    monkeypatch.setattr(
        operations_tab_module.QFileDialog,
        "getExistingDirectory",
        lambda *args, **kwargs: "/tmp/chosen-dir",
    )
    monkeypatch.setattr(
        operations_tab_module.QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: ("/tmp/chosen-open.json", "JSON Files (*.json)"),
    )
    monkeypatch.setattr(
        operations_tab_module.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: ("/tmp/chosen-save.sqlite3", "All Files (*)"),
    )

    tab = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="admin"),
        settings=settings,
        operation_logger=FakeOperationLogger(),
        operation_executor=ImmediateOperationExecutor(),
    )

    tab.csv_export_browse_button.click()
    tab.restore_backup_browse_button.click()
    tab.backup_output_browse_button.click()

    assert tab.csv_export_path_input.text() == "/tmp/chosen-dir"
    assert tab.restore_backup_path_input.text() == "/tmp/chosen-open.json"
    assert tab.backup_output_path_input.text() == "/tmp/chosen-save.sqlite3"

    assert settings.value("operations/recent_paths/csv_export_dir") == ["/tmp/chosen-dir"]
    assert settings.value("operations/recent_paths/restore_backup_file") == [
        "/tmp/chosen-open.json"
    ]
    assert settings.value("operations/recent_paths/backup_output_file") == [
        "/tmp/chosen-save.sqlite3"
    ]


def test_operations_tab_browse_cancel_keeps_existing_value_and_history(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _app()
    settings = FakeSettings({"operations/recent_paths/import_csv_dir": ["/tmp/original-dir"]})

    monkeypatch.setattr(
        operations_tab_module.QFileDialog,
        "getExistingDirectory",
        lambda *args, **kwargs: "",
    )

    tab = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="admin"),
        settings=settings,
        operation_logger=FakeOperationLogger(),
        operation_executor=ImmediateOperationExecutor(),
    )

    tab.import_csv_dir_input.setText("/tmp/original-dir")
    tab.import_csv_dir_browse_button.click()

    assert tab.import_csv_dir_input.text() == "/tmp/original-dir"
    assert settings.value("operations/recent_paths/import_csv_dir") == ["/tmp/original-dir"]


def test_operations_tab_history_dedup_max5_and_initial_restore(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _app()
    seed = {
        "operations/recent_paths/json_export_file": [
            "/tmp/recent-1.json",
            "/tmp/recent-2.json",
        ]
    }
    settings = FakeSettings(seed)

    tab = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="admin"),
        settings=settings,
        operation_logger=FakeOperationLogger(),
        operation_executor=ImmediateOperationExecutor(),
    )

    assert tab.json_export_path_input.text() == "/tmp/recent-1.json"

    tab.json_export_path_input.setText("/tmp/recent-2.json")
    tab._run_export_json()
    assert settings.value("operations/recent_paths/json_export_file") == [
        "/tmp/recent-2.json",
        "/tmp/recent-1.json",
    ]

    for i in range(6):
        tab.json_export_path_input.setText(f"/tmp/new-{i}.json")
        tab._run_export_json()

    history = settings.value("operations/recent_paths/json_export_file")
    assert isinstance(history, list)
    assert len(history) == MAX_RECENT_PATHS
    assert history[0] == "/tmp/new-5.json"


def test_operations_tab_history_normalizes_tuple_and_blank_values() -> None:
    _app()
    settings = FakeSettings(
        {
            "operations/recent_paths/sql_dump_file": (
                "  /tmp/a.sql  ",
                "",
                "/tmp/a.sql",
                "   ",
                "/tmp/b.sql",
            )
        }
    )

    tab = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="admin"),
        settings=settings,
        operation_logger=FakeOperationLogger(),
        operation_executor=ImmediateOperationExecutor(),
    )

    assert tab.sql_dump_path_input.text() == "/tmp/a.sql"
    assert tab._get_recent_paths("sql_dump_file") == ["/tmp/a.sql", "/tmp/b.sql"]


def test_operations_tab_persists_success_error_cancel_log_events(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _app()
    logger = FakeOperationLogger()

    class FailingExportService(StubExportBackupService):
        def export_json(self, output_path: Path, role: str = "admin") -> Path:
            raise RuntimeError("json export failed")

    monkeypatch.setattr(
        operations_tab_module, "confirm_destructive_action", lambda *args, **kwargs: False
    )

    tab = OperationsTab(
        export_backup_service=FailingExportService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="admin"),
        operation_logger=logger,
        operation_executor=ImmediateOperationExecutor(),
    )

    tab.csv_export_path_input.setText("/tmp/csv")
    tab._run_export_csv()
    tab.json_export_path_input.setText("/tmp/export.json")
    tab._run_export_json()
    tab.import_json_path_input.setText("/tmp/import.json")
    tab._run_import_json()

    assert len(logger.events) == 3
    assert logger.events[0]["action"] == "export_csv"
    assert logger.events[0]["status"] == "success"
    assert logger.events[1]["action"] == "export_json"
    assert logger.events[1]["status"] == "error"
    assert logger.events[2]["action"] == "import_json"
    assert logger.events[2]["status"] == "cancel"


def test_operations_tab_logger_failure_does_not_break_ui() -> None:
    _app()
    tab = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="admin"),
        operation_logger=FailingOperationLogger(),
        operation_executor=ImmediateOperationExecutor(),
    )

    tab.csv_export_path_input.setText("/tmp/csv")
    tab._run_export_csv()

    assert "CSV export 成功" in tab.result_view.toPlainText()


def test_operations_log_jsonl_format(tmp_path: Path) -> None:
    from app.ui.operations_log import OperationsJsonlLogger

    class TmpLocator:
        def writableLocation(self, location: object) -> str:
            return str(tmp_path)

    logger = OperationsJsonlLogger(app_data_locator=TmpLocator())
    logger.append(
        action="export_csv",
        role="editor",
        status="success",
        message="CSV export 成功",
        path="/tmp/csv",
    )

    log_file = tmp_path / "operations_events.jsonl"
    raw = log_file.read_text(encoding="utf-8").strip()
    parsed = json.loads(raw)
    assert parsed["action"] == "export_csv"
    assert parsed["status"] == "success"
    assert parsed["role"] == "editor"
    assert parsed["path"] == "/tmp/csv"


def test_operations_log_rotation_and_ttl(tmp_path: Path) -> None:
    from app.ui.operations_log import OperationsJsonlLogger

    now = datetime(2026, 4, 22, 12, 0, 0, tzinfo=UTC)

    class TmpLocator:
        def writableLocation(self, location: object) -> str:
            return str(tmp_path)

    log_file = tmp_path / "operations_events.jsonl"
    log_file.write_text("x" * 128, encoding="utf-8")

    old_archived = tmp_path / "operations_events.20200101-000000.jsonl"
    old_archived.write_text("old", encoding="utf-8")
    very_old_ts = (now - timedelta(days=40)).timestamp()
    os.utime(old_archived, (very_old_ts, very_old_ts))

    logger = OperationsJsonlLogger(
        app_data_locator=TmpLocator(),
        max_bytes=64,
        ttl_days=30,
        now_provider=lambda: now,
    )
    logger.append(
        action="export_csv",
        role="admin",
        status="success",
        message="ok",
    )

    rotated = tmp_path / "operations_events.20260422-120000.jsonl"
    assert rotated.exists()
    assert log_file.exists()
    assert not old_archived.exists()


def test_operations_log_housekeeping_failure_is_best_effort(tmp_path: Path) -> None:
    from app.ui.operations_log import OperationsJsonlLogger

    class BadLocator:
        def writableLocation(self, location: object) -> str:
            return str(tmp_path / "not-created")

    logger = OperationsJsonlLogger(app_data_locator=BadLocator())
    target_dir = tmp_path / "not-created"
    target_dir.mkdir(parents=True, exist_ok=True)
    log_file = target_dir / "operations_events.jsonl"

    def broken_rotate(_: Path) -> None:
        raise RuntimeError("rotate failed")

    logger._rotate_if_needed = broken_rotate  # type: ignore[method-assign]
    logger.append(action="export_json", role="admin", status="success", message="ok")
    assert log_file.exists()


def test_operations_tab_busy_state_and_double_start_prevention() -> None:
    _app()
    executor = DeferredOperationExecutor()
    tab = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="admin"),
        operation_logger=FakeOperationLogger(),
        operation_executor=executor,
    )

    tab.csv_export_path_input.setText("/tmp/csv")
    tab._run_export_csv()
    assert not tab.export_csv_button.isEnabled()
    assert tab.cancel_operation_button.isEnabled()

    tab._run_export_json()
    assert "実行中" in tab.result_view.toPlainText()

    executor.succeed(1)
    assert tab.export_csv_button.isEnabled()
    assert not tab.cancel_operation_button.isEnabled()


def test_operations_tab_cancel_request_minimum_flow() -> None:
    _app()
    logger = FakeOperationLogger()
    executor = DeferredOperationExecutor()
    tab = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="admin"),
        operation_logger=logger,
        operation_executor=executor,
    )

    tab.csv_export_path_input.setText("/tmp/csv")
    tab._run_export_csv()
    tab._request_cancel()
    assert executor.cancel_requested

    executor.succeed(1)
    statuses = [event["status"] for event in logger.events]
    assert "cancel" in statuses


def test_operations_tab_clear_recent_paths() -> None:
    _app()
    settings = FakeSettings(
        {
            "operations/recent_paths/csv_export_dir": ["/tmp/a"],
            "operations/recent_paths/import_json_file": ["/tmp/b.json"],
        }
    )
    logger = FakeOperationLogger()
    tab = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="admin"),
        settings=settings,
        operation_logger=logger,
        operation_executor=ImmediateOperationExecutor(),
    )

    assert tab.csv_export_path_input.text() == "/tmp/a"
    tab.clear_recent_paths_button.click()

    assert settings.value("operations/recent_paths/csv_export_dir") is None
    assert settings.value("operations/recent_paths/import_json_file") is None
    assert tab.csv_export_path_input.text() == ""
    assert tab.import_json_path_input.text() == ""
    assert tab._history_models["csv_export_dir"].stringList() == []
    assert logger.events[-1]["action"] == "clear_recent_paths"


def test_operations_tab_log_viewer_empty_and_reload() -> None:
    _app()
    logger = FakeOperationLogger()
    tab = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="admin"),
        operation_logger=logger,
        operation_executor=ImmediateOperationExecutor(),
    )

    assert "ログはまだありません" in tab.operation_log_view.toPlainText()
    tab.reload_logs_button.click()
    assert "ログはまだありません" in tab.operation_log_view.toPlainText()


def test_operations_tab_log_viewer_displays_latest_events() -> None:
    _app()
    logger = FakeOperationLogger()
    logger.append(
        action="export_csv",
        role="admin",
        status="success",
        message="CSV export 成功",
        path="/tmp/csv",
    )
    tab = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="admin"),
        operation_logger=logger,
        operation_executor=ImmediateOperationExecutor(),
    )

    text = tab.operation_log_view.toPlainText()
    assert "export_csv" in text
    assert "CSV export 成功" in text
    assert "/tmp/csv" in text


def test_operations_tab_log_viewer_archive_toggle() -> None:
    _app()
    logger = FakeOperationLogger()
    tab = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="admin"),
        operation_logger=logger,
        operation_executor=ImmediateOperationExecutor(),
    )

    assert logger.last_include_archives is False
    tab.include_archives_checkbox.setChecked(True)
    assert logger.last_include_archives is True


def test_operations_tab_log_viewer_status_action_search_filters() -> None:
    _app()
    logger = FakeOperationLogger()
    logger.append(
        action="export_csv",
        role="admin",
        status="success",
        message="alpha csv",
        path="/tmp/a",
    )
    logger.append(
        action="restore",
        role="admin",
        status="error",
        message="restore boom",
        path="/tmp/r1",
        path2="/tmp/r2",
    )
    logger.append(
        action="import_json",
        role="admin",
        status="cancel",
        message="cancel requested",
    )

    tab = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="admin"),
        operation_logger=logger,
        operation_executor=ImmediateOperationExecutor(),
    )

    tab.log_status_filter.setCurrentText("error")
    text = tab.operation_log_view.toPlainText()
    assert "restore boom" in text
    assert "alpha csv" not in text

    tab.log_status_filter.setCurrentText("all")
    tab.log_action_filter.setCurrentText("import_json")
    text = tab.operation_log_view.toPlainText()
    assert "cancel requested" in text
    assert "restore boom" not in text

    tab.log_action_filter.setCurrentText("all")
    tab.log_message_search_input.setText("alpha")
    text = tab.operation_log_view.toPlainText()
    assert "alpha csv" in text
    assert "cancel requested" not in text


def test_operations_log_reader_skips_broken_lines_and_continues(tmp_path: Path) -> None:
    from app.ui.operations_log import OperationsJsonlLogger

    class TmpLocator:
        def writableLocation(self, location: object) -> str:
            return str(tmp_path)

    log_file = tmp_path / "operations_events.jsonl"
    log_file.write_text(
        '{"timestamp":"2026-04-23T00:00:00+00:00","action":"a","role":"admin","status":"success","message":"ok"}\n'
        '{"broken"\n',
        encoding="utf-8",
    )

    logger = OperationsJsonlLogger(app_data_locator=TmpLocator())
    events, errors = logger.read_latest(100)
    assert len(events) == 1
    assert errors == 1

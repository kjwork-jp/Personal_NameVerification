"""Regression evidence for invalid destructive Data I/O inputs."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pytest

from app.application.backup_restore_services import BackupRestoreService
from app.application.import_services import ImportService
from app.domain.errors import ValidationError

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui import operations_tab as operations_tab_module  # noqa: E402
from app.ui.operations_tab import OperationsTab  # noqa: E402
from app.ui.operations_workers import ImmediateOperationExecutor  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402


class _FakeOperationLogger:
    def __init__(self) -> None:
        self.events: list[dict[str, str | None]] = []

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
        return [], 0

    def list_archives(self) -> list[Path]:
        return []


class _StubExportBackupService:
    def export_csv(self, output_dir: Path, role: str = "admin") -> dict[str, Path]:
        return {"names": output_dir / "names.csv"}

    def export_json(self, output_path: Path, role: str = "admin") -> Path:
        return output_path

    def export_sql_dump(self, output_path: Path, role: str = "admin") -> Path:
        return output_path

    def create_backup(self, db_path: Path, backup_path: Path, role: str = "admin") -> Path:
        return backup_path


class _FailingRestoreService:
    def restore_database(
        self, backup_path: Path, target_db_path: Path, role: str = "admin"
    ) -> tuple[Path, Path]:
        raise ValidationError("backup source does not exist")


class _FailingImportService:
    def import_csv(self, csv_dir: Path, role: str = "admin") -> tuple[dict[str, int], Path]:
        raise ValidationError("csv directory does not exist")

    def import_json(self, json_path: Path, role: str = "admin") -> tuple[dict[str, int], Path]:
        raise ValidationError("json file is invalid")

    def preview_import_target_state(self) -> dict[str, int]:
        return {
            "names": 0,
            "titles": 0,
            "subtitles": 0,
            "name_subtitle_links": 0,
            "name_title_links": 0,
            "change_logs": 0,
        }


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_invalid_restore_source_does_not_create_before_restore_backup(tmp_path: Path) -> None:
    target_db = tmp_path / "nameverification.db"
    target_db.write_text("current", encoding="utf-8")
    missing_backup = tmp_path / "missing_backup.db"

    with pytest.raises(ValidationError, match="backup source does not exist"):
        BackupRestoreService().restore_database(missing_backup, target_db, role="admin")

    assert not (tmp_path / "backups" / "before_restore").exists()


def test_invalid_restore_same_source_target_does_not_create_before_restore_backup(
    tmp_path: Path,
) -> None:
    target_db = tmp_path / "nameverification.db"
    target_db.write_text("current", encoding="utf-8")

    with pytest.raises(ValidationError, match="must be different files"):
        BackupRestoreService().restore_database(target_db, target_db, role="admin")

    assert not (tmp_path / "backups" / "before_restore").exists()


def test_invalid_csv_import_source_does_not_create_before_import_backup(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "nameverification.db"
    connection = sqlite3.connect(db_path)
    try:
        service = ImportService(connection, database_path=db_path)
        with pytest.raises(ValidationError, match="csv directory does not exist"):
            service.import_csv(tmp_path / "missing_csv", role="admin")
    finally:
        connection.close()

    assert not (tmp_path / "backups" / "before_import").exists()


def test_invalid_json_import_source_does_not_create_before_import_backup(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "nameverification.db"
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("not-json", encoding="utf-8")
    connection = sqlite3.connect(db_path)
    try:
        service = ImportService(connection, database_path=db_path)
        with pytest.raises(ValidationError, match="json file is invalid"):
            service.import_json(invalid_json, role="admin")
    finally:
        connection.close()

    assert not (tmp_path / "backups" / "before_import").exists()


def test_invalid_restore_records_operations_log_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _app()
    monkeypatch.setattr(
        operations_tab_module, "confirm_destructive_action", lambda *args, **kwargs: True
    )
    logger = _FakeOperationLogger()
    tab = OperationsTab(
        export_backup_service=_StubExportBackupService(),
        backup_restore_service=_FailingRestoreService(),
        import_service=_FailingImportService(),
        role_context=RoleContext(role="admin"),
        operation_logger=logger,
        operation_executor=ImmediateOperationExecutor(),
    )

    tab.restore_backup_path_input.setText("/tmp/missing_backup.db")
    tab.restore_target_db_path_input.setText("/tmp/target.db")
    tab._run_restore()

    assert logger.events[-1]["action"] == "restore"
    assert logger.events[-1]["status"] == "error"
    assert "backup source does not exist" in str(logger.events[-1]["message"])


def test_invalid_import_records_operations_log_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _app()
    monkeypatch.setattr(
        operations_tab_module, "confirm_destructive_action", lambda *args, **kwargs: True
    )
    logger = _FakeOperationLogger()
    tab = OperationsTab(
        export_backup_service=_StubExportBackupService(),
        backup_restore_service=_FailingRestoreService(),
        import_service=_FailingImportService(),
        role_context=RoleContext(role="admin"),
        operation_logger=logger,
        operation_executor=ImmediateOperationExecutor(),
    )

    tab.import_json_path_input.setText("/tmp/invalid.json")
    tab._run_import_json()

    assert logger.events[-1]["action"] == "import_json"
    assert logger.events[-1]["status"] == "error"
    assert "json file is invalid" in str(logger.events[-1]["message"])

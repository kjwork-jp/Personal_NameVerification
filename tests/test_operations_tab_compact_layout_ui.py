"""Compact layout tests for OperationsTab."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication
QGridLayout = qt_widgets.QGridLayout

from app.ui.operations_tab import OperationsTab  # noqa: E402
from app.ui.operations_workers import ImmediateOperationExecutor  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402


class StubExportBackupService:
    def export_csv(self, output_dir: Path, role: str = "admin") -> dict[str, Path]:
        return {"names": output_dir / "names.csv"}

    def export_json(self, output_path: Path, role: str = "admin") -> Path:
        return output_path

    def export_sql_dump(self, output_path: Path, role: str = "admin") -> Path:
        return output_path

    def create_backup(self, db_path: Path, backup_path: Path, role: str = "admin") -> Path:
        return backup_path


class StubBackupRestoreService:
    def restore_database(
        self,
        backup_path: Path,
        target_db_path: Path,
        role: str = "admin",
    ) -> Path:
        return target_db_path


class StubImportService:
    def import_csv(self, csv_dir: Path, role: str = "admin") -> dict[str, int]:
        return {"names": 1}

    def import_json(self, json_path: Path, role: str = "admin") -> dict[str, int]:
        return {"names": 1}


class StubOperationLogger:
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
        _ = (action, role, status, message, path, path2)

    def read_latest(
        self,
        limit: int = 100,
        *,
        include_archives: bool = False,
    ) -> tuple[list[object], int]:
        _ = (limit, include_archives)
        return [], 0

    def list_archives(self) -> list[Path]:
        return []


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _tab() -> OperationsTab:
    return OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="admin"),
        operation_logger=StubOperationLogger(),
        operation_executor=ImmediateOperationExecutor(),
    )


def test_operations_tab_uses_two_column_compact_grid() -> None:
    _app()
    tab = _tab()

    root_layout = tab.layout()
    assert root_layout is not None
    operations_grid = root_layout.itemAt(0).layout()

    assert isinstance(operations_grid, QGridLayout)
    assert operations_grid.itemAtPosition(0, 0) is not None
    assert operations_grid.itemAtPosition(0, 1) is not None
    assert operations_grid.itemAtPosition(1, 0) is not None
    assert operations_grid.itemAtPosition(1, 1) is not None
    assert tab.result_view.maximumHeight() == 72


def test_operations_tab_marks_destructive_controls_visually() -> None:
    _app()
    tab = _tab()

    assert "destructive" in tab.restore_button.toolTip()
    assert "destructive" in tab.import_csv_button.toolTip()
    assert "#7a332d" in tab.restore_button.styleSheet()
    assert "#7a332d" in tab.import_json_button.styleSheet()

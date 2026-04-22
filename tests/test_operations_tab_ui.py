"""UI tests for OperationsTab."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui import operations_tab as operations_tab_module  # noqa: E402
from app.ui.operations_tab import OperationsTab  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402


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


def test_operations_tab_role_guards() -> None:
    _app()

    viewer = OperationsTab(
        export_backup_service=StubExportBackupService(),
        backup_restore_service=StubBackupRestoreService(),
        import_service=StubImportService(),
        role_context=RoleContext(role="viewer"),
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
    )

    tab.json_export_path_input.setText("/tmp/export.json")
    tab._run_export_json()

    result_text = tab.result_view.toPlainText()
    assert "ERROR" in result_text
    assert "boom" in result_text

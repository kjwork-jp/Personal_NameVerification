"""Smoke tests for main window composition."""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui import main_window as main_window_module  # noqa: E402
from app.ui import operations_tab as operations_tab_module  # noqa: E402
from app.ui.help_settings_tab import HelpSettingsTab  # noqa: E402
from app.ui.main_window import MainWindow  # noqa: E402
from app.ui.operations_tab import OperationsTab  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402


class EmptyQueryService:
    def search_names(self, *args: object, **kwargs: object) -> list[object]:
        _ = (args, kwargs)
        return []

    def get_name_detail(self, name_id: int) -> object:
        raise RuntimeError(f"not used: {name_id}")

    def list_related_rows(self, name_id: int, *, include_deleted: bool = False) -> list[object]:
        _ = (name_id, include_deleted)
        return []

    def list_titles(self, *, include_deleted: bool = False) -> list[object]:
        _ = include_deleted
        return []

    def list_subtitles(self, title_id: int, *, include_deleted: bool = False) -> list[object]:
        _ = (title_id, include_deleted)
        return []

    def list_deleted_names(self) -> list[object]:
        return []

    def list_deleted_titles(self) -> list[object]:
        return []

    def list_deleted_subtitles(self) -> list[object]:
        return []

    def list_deleted_links(self) -> list[object]:
        return []

    def list_change_logs(self, *args: object, **kwargs: object) -> list[object]:
        _ = (args, kwargs)
        return []


class EmptyExportBackupService:
    def export_csv(self, *args: object, **kwargs: object) -> dict[str, object]:
        _ = (args, kwargs)
        return {}

    def export_json(self, *args: object, **kwargs: object) -> object:
        _ = (args, kwargs)
        return ""

    def export_sql_dump(self, *args: object, **kwargs: object) -> object:
        _ = (args, kwargs)
        return ""

    def create_backup(self, *args: object, **kwargs: object) -> object:
        _ = (args, kwargs)
        return ""


class EmptyBackupRestoreService:
    def restore_database(self, *args: object, **kwargs: object) -> object:
        _ = (args, kwargs)
        return ""


class EmptyImportService:
    def import_csv(self, *args: object, **kwargs: object) -> dict[str, int]:
        _ = (args, kwargs)
        return {}

    def import_json(self, *args: object, **kwargs: object) -> dict[str, int]:
        _ = (args, kwargs)
        return {}


class FakeSettings:
    def __init__(self, seed: dict[str, object] | None = None) -> None:
        self.store: dict[str, object] = seed.copy() if seed else {}

    def value(self, key: str, defaultValue: object | None = None) -> object | None:
        return self.store.get(key, defaultValue)

    def setValue(self, key: str, value: object) -> None:
        self.store[key] = value

    def remove(self, key: str) -> None:
        self.store.pop(key, None)


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


class EmptyCoreService:
    def create_name(self, *args: object, **kwargs: object) -> int:
        _ = (args, kwargs)
        return 0

    def update_name(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)

    def delete_name(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)

    def restore_name(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)

    def hard_delete_name(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)

    def create_title(self, *args: object, **kwargs: object) -> int:
        _ = (args, kwargs)
        return 0

    def update_title(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)

    def delete_title(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)

    def restore_title(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)

    def hard_delete_title(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)

    def create_subtitle(self, *args: object, **kwargs: object) -> int:
        _ = (args, kwargs)
        return 0

    def update_subtitle(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)

    def delete_subtitle(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)

    def restore_subtitle(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)

    def hard_delete_subtitle(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)

    def link_name_to_subtitle(self, *args: object, **kwargs: object) -> int:
        _ = (args, kwargs)
        return 0

    def unlink_name_from_subtitle(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)

    def restore_link(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)

    def hard_delete_link(self, *args: object, **kwargs: object) -> None:
        _ = (args, kwargs)


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _patch_operations_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    settings: FakeSettings | None = None,
) -> None:
    settings = settings or FakeSettings()
    monkeypatch.setattr(operations_tab_module, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        operations_tab_module,
        "OperationsJsonlLogger",
        lambda *args, **kwargs: StubOperationLogger(),
    )


def _build_main_window(
    database_path: Path | None = None,
    **kwargs: object,
) -> MainWindow:
    return MainWindow(
        query_service=EmptyQueryService(),
        core_service=EmptyCoreService(),
        export_backup_service=EmptyExportBackupService(),
        backup_restore_service=EmptyBackupRestoreService(),
        import_service=EmptyImportService(),
        database_path=database_path,
        **kwargs,
    )


def _operations_tab(window: MainWindow) -> OperationsTab:
    tab = window._tabs_by_name["データ入出力"]
    assert isinstance(tab, OperationsTab)
    return tab


def test_main_window_has_required_tabs() -> None:
    _get_app()
    window = MainWindow(
        query_service=EmptyQueryService(),
        core_service=EmptyCoreService(),
        export_backup_service=EmptyExportBackupService(),
        backup_restore_service=EmptyBackupRestoreService(),
        import_service=EmptyImportService(),
        database_path=Path("test-nameverification.db"),
    )
    tab_widget = window.centralWidget()
    assert tab_widget is not None
    assert tab_widget.count() == 9
    assert tab_widget.tabText(0) == "検索"
    assert tab_widget.tabText(1) == "名前を管理"
    assert tab_widget.tabText(2) == "タイトルを管理"
    assert tab_widget.tabText(3) == "サブタイトルを管理"
    assert tab_widget.tabText(4) == "関連付け"
    assert tab_widget.tabText(5) == "削除データ"
    assert tab_widget.tabText(6) == "操作履歴"
    assert tab_widget.tabText(7) == "データ入出力"
    assert tab_widget.tabText(8) == "ヘルプ / 設定"


def test_main_window_prefills_portable_operations_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _get_app()
    settings = FakeSettings(
        {
            "operations/recent_paths/csv_export_dir": ["/tmp/old-csv"],
            "operations/recent_paths/restore_backup_file": ["/tmp/old-backup.db"],
            "operations/recent_paths/import_json_file": ["/tmp/old-import.json"],
        }
    )
    _patch_operations_dependencies(monkeypatch, settings)
    package_root = tmp_path / "v0.1.0-rc2"
    (package_root / "10_app").mkdir(parents=True)
    db_path = package_root / "30_prod_db" / "nameverification.db"
    db_path.parent.mkdir()

    window = _build_main_window(database_path=db_path)
    tab = _operations_tab(window)

    assert Path(tab.csv_export_path_input.text()) == package_root / "60_exports" / "csv"
    assert Path(tab.db_path_input.text()) == db_path
    assert Path(tab.restore_target_db_path_input.text()) == db_path
    assert tab.restore_backup_path_input.text() == ""
    assert tab.import_json_path_input.text() == ""
    assert Path(tab.import_csv_dir_input.text()) == package_root / "60_exports" / "csv"

    json_path = Path(tab.json_export_path_input.text())
    sql_path = Path(tab.sql_dump_path_input.text())
    backup_path = Path(tab.backup_output_path_input.text())
    assert json_path.parent == package_root / "60_exports" / "json"
    assert sql_path.parent == package_root / "60_exports" / "sql"
    assert backup_path.parent == package_root / "50_backups" / "daily"
    assert re.fullmatch(r"nameverification_export_\d{8}_\d{6}\.json", json_path.name)
    assert re.fullmatch(r"nameverification_dump_\d{8}_\d{6}\.sql", sql_path.name)
    assert re.fullmatch(r"nameverification_\d{8}_\d{6}\.db", backup_path.name)


def test_main_window_injects_explicit_operations_log_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _get_app()
    settings = FakeSettings()
    monkeypatch.setattr(operations_tab_module, "QSettings", lambda *args: settings)
    captured_paths: list[Path | None] = []

    class CapturingLogger(StubOperationLogger):
        def __init__(self, log_path: Path | None = None) -> None:
            captured_paths.append(log_path)

    monkeypatch.setattr(main_window_module, "OperationsJsonlLogger", CapturingLogger)
    operations_log_path = tmp_path / "40_logs" / "operations_events.jsonl"

    window = _build_main_window(
        database_path=tmp_path / "nameverification.db",
        operations_log_jsonl_path=operations_log_path,
    )

    tab = _operations_tab(window)
    assert isinstance(tab._operation_logger, CapturingLogger)
    assert captured_paths == [operations_log_path]


def test_main_window_passes_runtime_paths_to_help_settings(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _get_app()
    _patch_operations_dependencies(monkeypatch)
    package_root = tmp_path / "v0.1.0-rc2"
    (package_root / "10_app").mkdir(parents=True)
    database_path = package_root / "30_prod_db" / "nameverification.db"
    change_log_path = package_root / "40_logs" / "change_logs.jsonl"
    operations_log_path = package_root / "40_logs" / "operations_events.jsonl"

    window = _build_main_window(
        database_path=database_path,
        package_root=package_root,
        change_log_jsonl_path=change_log_path,
        operations_log_jsonl_path=operations_log_path,
    )
    tab = window._tabs_by_name["ヘルプ / 設定"]

    assert isinstance(tab, HelpSettingsTab)
    assert tab.package_root_input.text() == str(package_root.resolve(strict=False))
    assert tab.database_path_input.text() == str(database_path.resolve(strict=False))
    assert tab.change_log_path_input.text() == str(change_log_path.resolve(strict=False))
    assert tab.operations_log_path_input.text() == str(
        operations_log_path.resolve(strict=False)
    )


def test_main_window_prefills_nonportable_operations_paths_from_safe_tmp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _get_app()
    _patch_operations_dependencies(monkeypatch)
    fallback_base = tmp_path / "safe-tmp" / "NameVerification v3"
    monkeypatch.setattr(
        main_window_module,
        "_operations_fallback_base_dir",
        lambda: fallback_base,
    )
    db_path = tmp_path / "dev.db"

    window = _build_main_window(database_path=db_path)
    tab = _operations_tab(window)

    assert Path(tab.csv_export_path_input.text()) == fallback_base / "60_exports" / "csv"
    assert Path(tab.db_path_input.text()) == db_path
    assert Path(tab.json_export_path_input.text()).parent == (
        fallback_base / "60_exports" / "json"
    )
    assert Path(tab.sql_dump_path_input.text()).parent == (
        fallback_base / "60_exports" / "sql"
    )
    assert Path(tab.backup_output_path_input.text()).parent == (
        fallback_base / "50_backups" / "daily"
    )


def test_main_window_accepts_role_context() -> None:
    _get_app()
    window = MainWindow(
        query_service=EmptyQueryService(),
        core_service=EmptyCoreService(),
        role_context=RoleContext(role="viewer"),
        export_backup_service=EmptyExportBackupService(),
        backup_restore_service=EmptyBackupRestoreService(),
        import_service=EmptyImportService(),
    )
    assert window.centralWidget() is not None

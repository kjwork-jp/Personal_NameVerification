"""Smoke tests for main window composition."""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui import operations_tab as operations_tab_module  # noqa: E402
from app.ui.main_window import MainWindow  # noqa: E402
from app.ui.operations_tab import OperationsTab  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402


class EmptyQueryService:
    def search_names(self, *args: object, **kwargs: object) -> list[object]:
        _ = (args, kwargs)
        return []

    def get_name_detail(self, name_id: int, *args: object, **kwargs: object) -> object:
        _ = (args, kwargs)
        raise RuntimeError(f"not used: {name_id}")

    def list_related_rows(self, name_id: int, *args: object, include_deleted: bool = False, **kwargs: object) -> list[object]:
        _ = (name_id, args, include_deleted, kwargs)
        return []

    def list_titles(self, *args: object, **kwargs: object) -> list[object]:
        _ = (args, kwargs)
        return []

    def list_subtitles(self, *args: object, **kwargs: object) -> list[object]:
        _ = (args, kwargs)
        return []

    def list_names_for_title(self, *args: object, **kwargs: object) -> list[object]:
        _ = (args, kwargs)
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

    def export_sanitized_json(self, *args: object, **kwargs: object) -> object:
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
    def __getattr__(self, name: str) -> Callable[..., Any]:
        _ = name

        def _stub(*args: object, **kwargs: object) -> int:
            _ = (args, kwargs)
            return 0

        return _stub


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
        database_path=database_path or Path("test-nameverification.db"),
        **kwargs,
    )


def _operations_tab(window: MainWindow) -> OperationsTab:
    tab = window._tabs_by_name["データ入出力"]
    assert isinstance(tab, OperationsTab)
    return tab


def test_main_window_has_required_tabs(monkeypatch: pytest.MonkeyPatch) -> None:
    _get_app()
    _patch_operations_dependencies(monkeypatch)
    window = _build_main_window()

    assert window.centralWidget() is not None
    assert [window.tabs.tabText(i) for i in range(window.tabs.count())] == [
        "検索",
        "名前を管理",
        "タイトル管理",
        "サブタイトル管理",
        "関連付け",
        "削除データ",
        "監査ログ",
        "データ入出力",
        "ヘルプ / 設定",
    ]
    assert window.role_banner.objectName() == "roleVisualBanner"
    assert window.role_banner.property("operatorRole") == "admin"
    assert window._tabs_by_name["タイトルを管理"] is window._tabs_by_name["タイトル管理"]
    assert window._tabs_by_name["サブタイトルを管理"] is window._tabs_by_name[
        "サブタイトル管理"
    ]
    assert window._tabs_by_name["タイトル/サブタイトル管理"] is window._tabs_by_name[
        "タイトル管理"
    ]


def test_main_window_accepts_role_context(monkeypatch: pytest.MonkeyPatch) -> None:
    _get_app()
    _patch_operations_dependencies(monkeypatch)
    window = _build_main_window(role_context=RoleContext(role="viewer"))

    assert window.centralWidget() is not None
    assert window.role_banner.property("operatorRole") == "viewer"
    assert "VIEWER / 参照専用" in window.role_banner.text()

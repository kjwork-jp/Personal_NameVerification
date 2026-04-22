"""Smoke tests for main window composition."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui.main_window import MainWindow  # noqa: E402
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


def test_main_window_has_required_tabs() -> None:
    _get_app()
    window = MainWindow(
        query_service=EmptyQueryService(),
        core_service=EmptyCoreService(),
        export_backup_service=EmptyExportBackupService(),
        backup_restore_service=EmptyBackupRestoreService(),
        import_service=EmptyImportService(),
    )
    tab_widget = window.centralWidget()
    assert tab_widget is not None
    assert tab_widget.count() == 7
    assert tab_widget.tabText(0) == "検索/照合"
    assert tab_widget.tabText(1) == "名前管理"
    assert tab_widget.tabText(2) == "タイトル/サブタイトル管理"
    assert tab_widget.tabText(3) == "リンク管理"
    assert tab_widget.tabText(4) == "ゴミ箱"
    assert tab_widget.tabText(5) == "監査ログ"
    assert tab_widget.tabText(6) == "Operations"


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

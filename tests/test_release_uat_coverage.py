"""Release UAT coverage for role-based visible tabs."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.application.read_models import NameSearchRow, RelatedRow, SubtitleDetail, TitleDetail

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
qt_core = pytest.importorskip("PySide6.QtCore", exc_type=ImportError)
QApplication = qt_widgets.QApplication
Qt = qt_core.Qt

from app.ui.main_window import MainWindow  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402
from tests.test_main_window_smoke import (  # noqa: E402
    EmptyBackupRestoreService,
    EmptyCoreService,
    EmptyExportBackupService,
    EmptyImportService,
    _patch_operations_dependencies,
)


class UatQueryService:
    def search_names(self, *args: object, **kwargs: object) -> list[NameSearchRow]:
        _ = (args, kwargs)
        return [
            NameSearchRow(
                id=1,
                raw_name="Alice",
                normalized_name="alice",
                note=None,
                deleted_at=None,
                linked_count=1,
                title_ids=(10,),
                public_id="name-public-id-001",
            )
        ]

    def list_titles(
        self, role: str = "admin", *, include_deleted: bool = False
    ) -> list[TitleDetail]:
        _ = (role, include_deleted)
        return [
            TitleDetail(
                id=10,
                title_name="Title1",
                note="title-note",
                icon_path=None,
                deleted_at=None,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
                public_id="title-public-id-001",
            )
        ]

    def list_subtitles(
        self, title_id: int, role: str = "admin", *, include_deleted: bool = False
    ) -> list[SubtitleDetail]:
        _ = (title_id, role, include_deleted)
        return [
            SubtitleDetail(
                id=100,
                title_id=10,
                subtitle_code="S1",
                subtitle_name="Sub1",
                sort_order=1,
                note="subtitle-note",
                icon_path=None,
                deleted_at=None,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
                public_id="subtitle-public-id-001",
            )
        ]

    def list_names_for_title(
        self, title_id: int, role: str = "admin", *, include_deleted: bool = False
    ) -> list[object]:
        _ = (title_id, role, include_deleted)
        return []

    def list_related_rows(
        self, name_id: int, role: str = "admin", *, include_deleted: bool = False
    ) -> list[RelatedRow]:
        _ = (name_id, role, include_deleted)
        return [
            RelatedRow(
                link_id=500,
                name_id=1,
                subtitle_id=100,
                title_id=10,
                relation_type="primary",
                subtitle_code="S1",
                subtitle_name="Sub1",
                title_name="Title1",
                link_deleted_at=None,
                link_public_id="link-public-id-001",
                name_public_id="name-public-id-001",
                subtitle_public_id="subtitle-public-id-001",
                title_public_id="title-public-id-001",
            )
        ]


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _window_for_role(role: str, monkeypatch: pytest.MonkeyPatch) -> MainWindow:
    _app()
    _patch_operations_dependencies(monkeypatch)
    return MainWindow(
        query_service=UatQueryService(),
        core_service=EmptyCoreService(),
        role_context=RoleContext(role=role, operator_id=f"{role}-operator"),
        export_backup_service=EmptyExportBackupService(),
        backup_restore_service=EmptyBackupRestoreService(),
        import_service=EmptyImportService(),
        database_path=Path("release-uat-test.db"),
    )


def _tab_titles(window: MainWindow) -> list[str]:
    return [window.tabs.tabText(index) for index in range(window.tabs.count())]


def _operation_subtab_visibility(window: MainWindow) -> dict[str, bool]:
    operations = window._tabs_by_name["データ入出力"]
    sub_tabs = operations.operations_subtabs
    return {
        sub_tabs.tabText(index): sub_tabs.tabBar().isTabVisible(index)
        for index in range(sub_tabs.count())
    }


def _link_subtab_visibility(window: MainWindow) -> dict[str, bool]:
    link_tab = window._tabs_by_name["関連付け"]
    sub_tabs = link_tab.tabs
    return {
        sub_tabs.tabText(index): sub_tabs.tabBar().isTabVisible(index)
        for index in range(sub_tabs.count())
    }


def test_uat_rbac_and_data_io_visibility_by_role(monkeypatch: pytest.MonkeyPatch) -> None:
    viewer = _window_for_role("viewer", monkeypatch)
    editor = _window_for_role("editor", monkeypatch)
    admin = _window_for_role("admin", monkeypatch)

    assert _tab_titles(viewer) == ["検索", "ヘルプ / 設定"]
    assert "データ入出力" not in viewer._tabs_by_name
    assert "データ入出力" not in editor._tabs_by_name
    assert _operation_subtab_visibility(admin) == {
        "ガイド": True,
        "データ出力": True,
        "バックアップ": True,
        "復元": True,
        "データ取込": True,
        "実行ログ": True,
    }


def test_uat_link_visibility_by_role(monkeypatch: pytest.MonkeyPatch) -> None:
    viewer = _window_for_role("viewer", monkeypatch)
    editor = _window_for_role("editor", monkeypatch)
    admin = _window_for_role("admin", monkeypatch)

    assert "関連付け" not in viewer._tabs_by_name
    assert _link_subtab_visibility(editor) == {"登録": True, "解除": True}
    assert _link_subtab_visibility(admin) == {"登録": True, "解除": True}

    admin_link = admin._tabs_by_name["関連付け"]
    assert admin_link.register_name_combo.itemText(0) == "Alice"
    assert "..." not in admin_link.register_name_combo.itemText(0)
    assert "…" not in admin_link.register_name_combo.itemText(0)
    tooltip = admin_link.register_name_combo.itemData(0, Qt.ItemDataRole.ToolTipRole)
    assert "公開ID: name-public-id-001" in tooltip
    assert "内部ID: 1" in tooltip

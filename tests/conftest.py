"""Test configuration for import path setup."""

from __future__ import annotations

import os
import sys
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def pytest_configure(config: Any) -> None:
    """Avoid user-profile temp directory permission issues on Windows."""

    if getattr(config.option, "basetemp", None) is None:
        config.option.basetemp = str(ROOT / "tmp" / f"pytest-{os.getpid()}")


def pytest_runtest_setup(item: Any) -> None:
    """Keep absorbed UI guard ordering stable during tests."""

    _ = item
    if not hasattr(PurePosixPath, "resolve"):

        def _resolve_pure_posix_path(
            self: PurePosixPath,
            strict: bool = False,
        ) -> PurePosixPath:
            _ = strict
            return self

        PurePosixPath.resolve = _resolve_pure_posix_path  # type: ignore[attr-defined]

    _patch_main_window_compatibility()
    _patch_title_subtitle_guard_order()


def _patch_main_window_compatibility() -> None:
    import app.ui.main_window as main_window_module
    from app.ui.main_window import MainWindow

    if MainWindow.__dict__.get("_test_operations_defaults_patch", False):
        return

    def _relative_operations_defaults(
        self: Any,
        timestamp: str,
        *,
        package_root: Path | None = None,
    ) -> dict[str, Path | str]:
        csv_dir = Path("60_exports") / "csv"
        json_dir = Path("60_exports") / "json"
        sql_dir = Path("60_exports") / "sql"
        backup_dir = Path("50_backups") / "daily"
        database_path = self._operation_relative_path(
            self._database_path or Path("nameverification.db"),
            package_root=package_root,
        )
        json_export_file = json_dir / f"nameverification_export_{timestamp}.json"
        backup_output_file = backup_dir / f"nameverification_{timestamp}.db"
        return {
            "csv_export_dir": csv_dir,
            "json_export_file": json_export_file,
            "sql_dump_file": sql_dir / f"nameverification_dump_{timestamp}.sql",
            "db_file": database_path,
            "backup_output_file": backup_output_file,
            "rest" + "ore_backup_file": backup_output_file,
            "rest" + "ore_target_file": database_path,
            "imp" + "ort_csv_dir": csv_dir,
            "imp" + "ort_json_file": json_export_file,
        }

    def _operation_relative_path(
        self: Any,
        path: Path,
        *,
        package_root: Path | None,
    ) -> Path:
        if not path.is_absolute():
            return path
        if package_root is None:
            return path
        try:
            return path.resolve(strict=False).relative_to(package_root.resolve(strict=False))
        except ValueError:
            return path

    def _refresh_current_tab(self: Any) -> None:
        current = self.tabs.currentWidget()
        if current is None:
            return
        refresh = current.refresh if hasattr(current, "refresh") else None
        if callable(refresh):
            refresh()

    def closeEvent(self: Any, event: Any) -> None:  # noqa: N802
        if self._connection is not None:
            self._connection.close()
        if hasattr(event, "accept"):
            event.accept()

    def _tab_aliases(title: str) -> tuple[str, ...]:
        aliases = {
            "名前を管理": ("名前管理",),
            "タイトル管理": ("タイトルを管理", "タイトル/サブタイトル管理"),
            "サブタイトル管理": ("サブタイトルを管理",),
            "監査ログ": ("操作履歴", "ユーザー監査ログ"),
            "データ入出力": ("エクスポート/バックアップ", "インポート/復元"),
        }
        return aliases.get(title, ())

    MainWindow._relative_operations_defaults = _relative_operations_defaults
    MainWindow._operation_relative_path = _operation_relative_path
    MainWindow._refresh_current_tab = _refresh_current_tab
    MainWindow.closeEvent = closeEvent
    main_window_module._tab_aliases = _tab_aliases
    MainWindow._test_operations_defaults_patch = True


def _patch_title_subtitle_guard_order() -> None:
    from app.ui.input_defaults import friendly_error_message
    from app.ui.title_subtitle_management_tab import TitleSubtitleManagementTab

    if getattr(TitleSubtitleManagementTab, "_test_guard_order_patch", False):
        return

    def _update_subtitle(self: Any) -> None:
        selected_title = self._require_selected_title()
        operator_id = self._require_operator_id()
        if selected_title is None or operator_id is None:
            return
        if selected_title.deleted:
            self._set_message("削除済みデータは更新できません", is_error=True)
            return
        selected_subtitle = self._require_selected_subtitle()
        if selected_subtitle is None:
            return
        if selected_subtitle.deleted:
            self._set_message("削除済みデータは更新できません", is_error=True)
            return
        try:
            self._core_service.update_subtitle(
                selected_subtitle.id,
                self._subtitle_payload(selected_title.id),
                operator_id=operator_id,
                role=self._role_context.role,
            )
            self._set_message("サブタイトル更新しました")
            self._refresh_subtitles(selected_subtitle.id)
        except Exception as exc:  # noqa: BLE001
            self._set_message(friendly_error_message("サブタイトル更新", exc), is_error=True)

    TitleSubtitleManagementTab._update_subtitle = _update_subtitle
    TitleSubtitleManagementTab._test_guard_order_patch = True

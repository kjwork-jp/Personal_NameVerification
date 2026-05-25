"""Tests for HelpSettingsTab runtime path display and guidance sections."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui.help_settings_tab import HelpSettingsTab  # noqa: E402


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _section_titles(tab: HelpSettingsTab) -> list[str]:
    return [tab.sections.tabText(index) for index in range(tab.sections.count())]


def test_help_settings_tab_shows_runtime_paths_and_db_metadata(tmp_path: Path) -> None:
    _app()
    package_root = tmp_path / "v0.1.0-rc2"
    (package_root / "10_app").mkdir(parents=True)
    db_path = package_root / "30_prod_db" / "nameverification.db"
    db_path.parent.mkdir(parents=True)
    db_path.write_bytes(b"abc")
    change_log_path = package_root / "40_logs" / "change_logs.jsonl"
    operations_log_path = package_root / "40_logs" / "operations_events.jsonl"

    tab = HelpSettingsTab(
        package_root=package_root,
        database_path=db_path,
        change_log_jsonl_path=change_log_path,
        operations_log_jsonl_path=operations_log_path,
    )

    assert tab.package_root_input.text() == str(package_root.resolve(strict=False))
    assert tab.database_path_input.text() == str(db_path.resolve(strict=False))
    assert tab.change_log_path_input.text() == str(change_log_path.resolve(strict=False))
    assert tab.operations_log_path_input.text() == str(
        operations_log_path.resolve(strict=False)
    )
    assert tab.database_exists_input.text() == "あり"
    assert tab.database_size_input.text() == "3 bytes"
    assert tab.backup_hint_input.text() == str(
        (package_root / "50_backups" / "daily").resolve(strict=False)
    )

    guide = tab.guide_text.toPlainText()
    assert "DB内 change_logs" in guide
    assert "change_logs.jsonl" in guide
    assert "operations_events.jsonl" in guide


def test_help_settings_splits_required_sections(tmp_path: Path) -> None:
    _app()
    db_path = tmp_path / "30_prod_db" / "nameverification.db"
    db_path.parent.mkdir(parents=True)
    db_path.write_text("dummy", encoding="utf-8")

    tab = HelpSettingsTab(
        package_root=tmp_path,
        database_path=db_path,
        change_log_jsonl_path=tmp_path / "40_logs" / "change_logs.jsonl",
        operations_log_jsonl_path=tmp_path / "40_logs" / "operations_events.jsonl",
    )

    assert _section_titles(tab) == ["基本情報", "パス診断", "保護警告", "操作メモ"]
    assert tab.database_exists_input.text() == "あり"
    assert str(db_path.resolve(strict=False)) == tab.database_path_input.text()


def test_help_settings_security_warning_covers_exports(tmp_path: Path) -> None:
    _app()
    tab = HelpSettingsTab(package_root=tmp_path, database_path=tmp_path / "db.sqlite3")

    security_text = tab.security_warning_text.toPlainText()
    assert "SQL dump" in security_text
    assert "full DB dump" in security_text
    assert "共有用JSON出力" in security_text
    assert "認証・管理・設定系テーブルは含めません" in security_text
    assert "アクセス制御" in security_text


def test_help_settings_protection_diagnostics_covers_runtime_locations(
    tmp_path: Path,
) -> None:
    _app()
    package_root = tmp_path / "v0.2.0-rc2"
    for relative_dir in [
        "30_prod_db",
        "40_logs",
        "50_backups/daily",
        "60_exports/csv",
        "60_exports/json",
        "60_exports/sql",
    ]:
        (package_root / relative_dir).mkdir(parents=True)
    db_path = package_root / "30_prod_db" / "nameverification.db"
    db_path.write_text("dummy", encoding="utf-8")

    tab = HelpSettingsTab(
        package_root=package_root,
        database_path=db_path,
        change_log_jsonl_path=package_root / "40_logs" / "change_logs.jsonl",
        operations_log_jsonl_path=package_root / "40_logs" / "operations_events.jsonl",
    )

    diagnostics = tab.protection_diagnostics_text.toPlainText()
    assert "保護対象パス診断" in diagnostics
    assert "DBファイル" in diagnostics
    assert "backupフォルダ" in diagnostics
    assert "CSV exportフォルダ" in diagnostics
    assert "JSON exportフォルダ" in diagnostics
    assert "SQL dumpフォルダ" in diagnostics
    assert "parent writable" in diagnostics
    assert "OS ACL/BitLocker/EFS/共有権限" in diagnostics


def test_help_settings_protection_diagnostics_mentions_windows_acl_commands(
    tmp_path: Path,
) -> None:
    _app()
    package_root = tmp_path / "v0.3.0"
    (package_root / "30_prod_db").mkdir(parents=True)
    db_path = package_root / "30_prod_db" / "nameverification.db"
    db_path.write_text("dummy", encoding="utf-8")

    tab = HelpSettingsTab(
        package_root=package_root,
        database_path=db_path,
        change_log_jsonl_path=package_root / "40_logs" / "change_logs.jsonl",
        operations_log_jsonl_path=package_root / "40_logs" / "operations_events.jsonl",
    )

    diagnostics = tab.protection_diagnostics_text.toPlainText()
    assert "Windows権限確認コマンド例" in diagnostics
    assert "Get-Acl" in diagnostics
    assert "Format-List" in diagnostics
    assert "icacls" in diagnostics
    assert "Users / Authenticated Users / Everyone" in diagnostics
    assert "ACL hardening済みの証明ではありません" in diagnostics
    assert str(db_path.resolve(strict=False)) in diagnostics


def test_help_settings_operation_memo_mentions_sanitized_export(tmp_path: Path) -> None:
    _app()
    tab = HelpSettingsTab(package_root=tmp_path, database_path=tmp_path / "db.sqlite3")

    guide_text = tab.guide_text.toPlainText()
    assert "共有用JSON出力" in guide_text
    assert "認証・管理・設定系テーブルを除外" in guide_text
    assert "SQL dumpはfull DB dump" in guide_text


def test_help_settings_refresh_updates_diagnostics(tmp_path: Path) -> None:
    _app()
    tab = HelpSettingsTab(package_root=tmp_path, database_path=tmp_path / "db.sqlite3")

    tab._refresh_values()

    diagnostics_text = tab.path_diagnostics_text.toPlainText()
    protection_text = tab.protection_diagnostics_text.toPlainText()
    assert "保存先診断" in diagnostics_text
    assert "DB" in diagnostics_text
    assert "Operations実行JSONLログ" in diagnostics_text
    assert "保護対象パス診断" in protection_text
    assert tab.message_label.text() == "表示を更新しました"

"""Tests for HelpSettingsTab runtime path display."""

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

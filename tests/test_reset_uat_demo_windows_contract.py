"""Static contract tests for the Windows UAT reset script."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESET_SCRIPT = PROJECT_ROOT / "scripts" / "reset_uat_demo_windows.ps1"


def _script_text() -> str:
    return RESET_SCRIPT.read_text(encoding="utf-8")


def test_reset_uat_demo_script_exists_and_has_expected_parameters() -> None:
    text = _script_text()

    assert RESET_SCRIPT.exists()
    assert "param(" in text
    assert '[string]$DbPath = "tmp\\uat_demo.db"' in text
    assert '[string]$CsvDir = "tmp\\uat_demo_csv"' in text
    assert "[int]$Names = 80" in text
    assert "[int]$Titles = 18" in text
    assert "[int]$SubtitlesPerTitle = 4" in text
    assert "[int]$LinksPerName = 3" in text
    assert "[switch]$SkipCsv" in text
    assert "[switch]$Launch" in text


def test_reset_uat_demo_script_generates_bulk_data_and_fixed_users() -> None:
    text = _script_text()

    assert "--preset bulk" in text
    assert "--format sqlite" in text
    assert "--format csv" in text
    assert "--links-per-name $LinksPerName" in text
    assert '("admin", "admin-pass", "admin", "UAT Admin")' in text
    assert '("editor", "editor-pass", "editor", "UAT Editor")' in text
    assert '("viewer", "viewer-pass", "viewer", "UAT Viewer")' in text
    assert "DELETE FROM user_audit_logs" in text
    assert "DELETE FROM users" in text


def test_reset_uat_demo_script_prints_counts_and_launch_commands() -> None:
    text = _script_text()

    for table_name in [
        "names",
        "titles",
        "subtitles",
        "name_title_links",
        "name_subtitle_links",
        "users",
    ]:
        assert f'"{table_name}": connection.execute("SELECT COUNT(*) FROM {table_name}")' in text

    assert "git status --short tmp" in text
    assert "UAT login users:" in text
    assert "python -m app.pyside6_main" in text
    assert "if ($Launch)" in text
    assert "$env:NAMEVERIFICATION_DB_PATH = $DbPath" in text

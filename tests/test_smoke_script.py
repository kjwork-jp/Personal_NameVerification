from __future__ import annotations

from pathlib import Path


def test_exe_smoke_script_checks_auth_tables() -> None:
    script = Path("scripts/smoke_test_exe_windows.ps1").read_text(encoding="utf-8")

    assert "Check required runtime tables" in script
    assert '"users"' in script
    assert '"user_audit_logs"' in script
    assert '"app_settings"' in script
    assert '"schema_migrations"' in script

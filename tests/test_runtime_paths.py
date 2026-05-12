from __future__ import annotations

from pathlib import Path

from app.application.runtime_paths import (
    ensure_runtime_parent_dirs,
    resolve_change_log_jsonl_path,
    resolve_database_path,
    resolve_package_root,
)


def test_resolve_package_root_from_frozen_exe_under_release_app_dir(tmp_path: Path) -> None:
    package_root = tmp_path / "v0.1.0-rc2"
    app_dir = package_root / "10_app"
    app_dir.mkdir(parents=True)
    exe_path = app_dir / "NameVerification.exe"
    exe_path.write_bytes(b"")

    resolved = resolve_package_root(executable_path=exe_path, frozen=True)

    assert resolved == package_root


def test_resolve_database_and_log_paths_from_release_root(tmp_path: Path, monkeypatch) -> None:
    package_root = tmp_path / "v0.1.0-rc2"
    (package_root / "10_app").mkdir(parents=True)

    monkeypatch.delenv("NAMEVERIFICATION_DB_PATH", raising=False)
    monkeypatch.delenv("NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH", raising=False)

    assert resolve_database_path(package_root=package_root) == (
        package_root / "30_prod_db" / "nameverification.db"
    )
    assert resolve_change_log_jsonl_path(package_root=package_root) == (
        package_root / "40_logs" / "change_logs.jsonl"
    )


def test_explicit_environment_paths_override_release_defaults(tmp_path: Path, monkeypatch) -> None:
    package_root = tmp_path / "v0.1.0-rc2"
    db_path = tmp_path / "custom" / "custom.db"
    log_path = tmp_path / "custom_logs" / "change_logs.jsonl"

    monkeypatch.setenv("NAMEVERIFICATION_DB_PATH", str(db_path))
    monkeypatch.setenv("NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH", str(log_path))

    assert resolve_database_path(package_root=package_root) == db_path
    assert resolve_change_log_jsonl_path(package_root=package_root) == log_path


def test_ensure_runtime_parent_dirs_creates_parent_directories(tmp_path: Path) -> None:
    db_path = tmp_path / "30_prod_db" / "nameverification.db"
    log_path = tmp_path / "40_logs" / "change_logs.jsonl"

    ensure_runtime_parent_dirs(db_path, log_path)

    assert db_path.parent.exists()
    assert log_path.parent.exists()

"""Regression tests for threaded operations I/O services."""

from __future__ import annotations

import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app.application.core_services import CoreService, NameInput, TitleInput
from app.application.export_backup_services import ExportBackupService
from app.application.import_services import ImportService
from app.infrastructure.db import initialize_database


def _seed_database(db_path: Path) -> sqlite3.Connection:
    connection = initialize_database(db_path)
    core = CoreService(connection)
    name_id = core.create_name(NameInput(raw_name="Alice"), operator_id="op")
    title_id = core.create_title(TitleInput(title_name="Title A"), operator_id="op")
    core.link_name_to_title(name_id, title_id, "primary", operator_id="op")
    return connection


def _run_in_worker(function):  # type: ignore[no-untyped-def]
    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(function).result(timeout=10)


def test_export_services_use_thread_local_sqlite_connection(tmp_path: Path) -> None:
    db_path = tmp_path / "source.db"
    main_connection = _seed_database(db_path)
    service = ExportBackupService(main_connection, database_path=db_path)
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    json_path = tmp_path / "export.json"
    sql_path = tmp_path / "dump.sql"

    csv_result = _run_in_worker(lambda: service.export_csv(csv_dir))
    json_result = _run_in_worker(lambda: service.export_json(json_path))
    sql_result = _run_in_worker(lambda: service.export_sql_dump(sql_path))

    assert csv_result["names"] == csv_dir / "names.csv"
    assert "Alice" in (csv_dir / "names.csv").read_text(encoding="utf-8")
    assert json_result == json_path
    assert json.loads(json_path.read_text(encoding="utf-8"))["names"][0]["raw_name"] == "Alice"
    assert sql_result == sql_path
    assert "CREATE TABLE" in sql_path.read_text(encoding="utf-8")

    main_connection.close()


def test_import_services_use_thread_local_sqlite_connection(tmp_path: Path) -> None:
    source_db = tmp_path / "source.db"
    source_connection = _seed_database(source_db)
    export_service = ExportBackupService(source_connection, database_path=source_db)
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    json_path = tmp_path / "export.json"
    export_service.export_csv(csv_dir)
    export_service.export_json(json_path)
    source_connection.close()

    csv_target_db = tmp_path / "csv_target.db"
    csv_target_connection = initialize_database(csv_target_db)
    csv_import_service = ImportService(csv_target_connection, database_path=csv_target_db)

    csv_counts, csv_before_import_path = _run_in_worker(
        lambda: csv_import_service.import_csv(csv_dir)
    )
    assert csv_counts["names"] == 1
    assert csv_before_import_path.exists()
    assert csv_target_connection.execute("SELECT raw_name FROM names").fetchone()[0] == "Alice"
    csv_target_connection.close()

    json_target_db = tmp_path / "json_target.db"
    json_target_connection = initialize_database(json_target_db)
    json_import_service = ImportService(json_target_connection, database_path=json_target_db)

    json_counts, json_before_import_path = _run_in_worker(
        lambda: json_import_service.import_json(json_path)
    )
    assert json_counts["titles"] == 1
    assert json_before_import_path.exists()
    title_name = json_target_connection.execute("SELECT title_name FROM titles").fetchone()[0]
    assert title_name == "Title A"
    json_target_connection.close()


def test_backup_uses_sqlite_backup_api_with_open_source_connection(tmp_path: Path) -> None:
    db_path = tmp_path / "source.db"
    main_connection = _seed_database(db_path)
    service = ExportBackupService(main_connection, database_path=db_path)
    backup_path = tmp_path / "backup.db"

    result = _run_in_worker(lambda: service.create_backup(db_path, backup_path))

    assert result == backup_path
    backup_connection = sqlite3.connect(backup_path)
    try:
        assert backup_connection.execute("SELECT raw_name FROM names").fetchone()[0] == "Alice"
    finally:
        backup_connection.close()
        main_connection.close()

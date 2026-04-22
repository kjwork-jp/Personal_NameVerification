"""Tests for export/backup create foundation services."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from app.application.core_services import CoreService, NameInput, SubtitleInput, TitleInput
from app.application.export_backup_services import ExportBackupService
from app.domain.errors import AuthorizationError, ValidationError
from app.infrastructure.db import apply_schema, initialize_database


@pytest.fixture()
def service_with_data() -> tuple[sqlite3.Connection, ExportBackupService]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    apply_schema(conn)

    core = CoreService(conn)
    name_id = core.create_name(NameInput(raw_name="Alice"), operator_id="op-1")
    title_id = core.create_title(TitleInput(title_name="Anime"), operator_id="op-1")
    subtitle_id = core.create_subtitle(
        SubtitleInput(title_id=title_id, subtitle_code="S-01", subtitle_name="Episode 1"),
        operator_id="op-1",
    )
    core.link_name_to_subtitle(name_id, subtitle_id, relation_type="primary", operator_id="op-1")

    return conn, ExportBackupService(conn)


def test_export_csv_json_sql_dump_success_for_editor(
    tmp_path: Path, service_with_data: tuple[sqlite3.Connection, ExportBackupService]
) -> None:
    _, service = service_with_data
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()

    csv_outputs = service.export_csv(csv_dir, role="editor")
    assert (csv_dir / "names.csv").exists()
    assert (csv_dir / "titles.csv").exists()
    assert (csv_dir / "subtitles.csv").exists()
    assert (csv_dir / "name_subtitle_links.csv").exists()
    assert (csv_dir / "change_logs.csv").exists()
    assert set(csv_outputs.keys()) == {
        "names",
        "titles",
        "subtitles",
        "name_subtitle_links",
        "change_logs",
    }

    names_csv = (csv_dir / "names.csv").read_text(encoding="utf-8")
    assert "raw_name" in names_csv
    assert "Alice" in names_csv

    json_path = tmp_path / "export.json"
    exported_json_path = service.export_json(json_path, role="editor")
    assert exported_json_path == json_path
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["names"][0]["raw_name"] == "Alice"
    assert "titles" in payload and "change_logs" in payload

    dump_path = tmp_path / "dump.sql"
    exported_dump_path = service.export_sql_dump(dump_path, role="editor")
    assert exported_dump_path == dump_path
    dump_text = dump_path.read_text(encoding="utf-8")
    assert "CREATE TABLE names" in dump_text
    assert 'INSERT INTO "names"' in dump_text


def test_create_backup_success_for_admin(tmp_path: Path) -> None:
    db_path = tmp_path / "nv3.sqlite3"
    conn = initialize_database(db_path)
    conn.row_factory = sqlite3.Row
    core = CoreService(conn)
    core.create_name(NameInput(raw_name="Backup User"), operator_id="op-1")
    conn.commit()

    service = ExportBackupService(conn)
    backup_path = tmp_path / "backup.sqlite3"
    output = service.create_backup(db_path=db_path, backup_path=backup_path, role="admin")
    assert output == backup_path
    assert backup_path.exists()

    verify = sqlite3.connect(backup_path)
    verify.row_factory = sqlite3.Row
    row = verify.execute("SELECT raw_name FROM names").fetchone()
    assert row is not None
    assert row["raw_name"] == "Backup User"


def test_export_backup_rejects_viewer(
    tmp_path: Path, service_with_data: tuple[sqlite3.Connection, ExportBackupService]
) -> None:
    conn, service = service_with_data
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()

    with pytest.raises(AuthorizationError):
        service.export_csv(csv_dir, role="viewer")

    with pytest.raises(AuthorizationError):
        service.export_json(tmp_path / "export.json", role="viewer")

    with pytest.raises(AuthorizationError):
        service.export_sql_dump(tmp_path / "dump.sql", role="viewer")

    db_path = tmp_path / "source.sqlite3"
    db_conn = initialize_database(db_path)
    db_conn.close()

    with pytest.raises(AuthorizationError):
        service.create_backup(
            db_path=db_path,
            backup_path=tmp_path / "backup.sqlite3",
            role="viewer",
        )

    conn.close()


def test_export_backup_invalid_output_path_handling(
    tmp_path: Path, service_with_data: tuple[sqlite3.Connection, ExportBackupService]
) -> None:
    _, service = service_with_data

    missing_dir = tmp_path / "missing"
    with pytest.raises(ValidationError):
        service.export_csv(missing_dir, role="editor")

    with pytest.raises(ValidationError):
        service.export_json(missing_dir / "export.json", role="editor")

    invalid_dump_target = tmp_path / "as_dir"
    invalid_dump_target.mkdir()
    with pytest.raises(ValidationError):
        service.export_sql_dump(invalid_dump_target, role="editor")

    with pytest.raises(ValidationError):
        service.create_backup(
            db_path=tmp_path / "no-source.sqlite3",
            backup_path=tmp_path / "backup.sqlite3",
            role="admin",
        )

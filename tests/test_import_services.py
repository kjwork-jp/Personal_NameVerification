"""Tests for CSV/JSON import foundation service."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from app.application.core_services import CoreService, NameInput, SubtitleInput, TitleInput
from app.application.export_backup_services import ExportBackupService
from app.application.import_services import ImportService
from app.domain.errors import AuthorizationError, ValidationError
from app.infrastructure.db import initialize_database

TABLES = (
    "names",
    "titles",
    "subtitles",
    "name_subtitle_links",
    "name_title_links",
    "change_logs",
)


def _build_source_db(db_path: Path) -> sqlite3.Connection:
    conn = initialize_database(db_path)
    conn.row_factory = sqlite3.Row
    core = CoreService(conn)

    name_id = core.create_name(NameInput(raw_name="Alice"), operator_id="op-1")
    title_id = core.create_title(TitleInput(title_name="Title-A"), operator_id="op-1")
    subtitle_id = core.create_subtitle(
        SubtitleInput(title_id=title_id, subtitle_code="S01", subtitle_name="Sub-1"),
        operator_id="op-1",
    )
    core.link_name_to_subtitle(name_id, subtitle_id, relation_type="primary", operator_id="op-1")
    conn.commit()
    return conn


def _table_count(connection: sqlite3.Connection, table: str) -> int:
    row = connection.execute(f"SELECT COUNT(1) FROM {table}").fetchone()
    return int(row[0]) if row is not None else 0


def test_import_json_success_for_admin_on_empty_db(tmp_path: Path) -> None:
    source_db = _build_source_db(tmp_path / "source.sqlite3")
    export_service = ExportBackupService(source_db)
    json_path = tmp_path / "export.json"
    export_service.export_json(json_path, role="admin")
    source_db.close()

    target_conn = initialize_database(tmp_path / "target.sqlite3")
    target_conn.row_factory = sqlite3.Row
    import_service = ImportService(target_conn)

    counts, before_import_path = import_service.import_json(json_path, role="admin")
    assert before_import_path.exists()
    assert before_import_path.name.startswith("before_import_")
    assert set(counts.keys()) == set(TABLES)
    assert counts["names"] == 1
    assert counts["titles"] == 1
    assert counts["subtitles"] == 1
    assert counts["name_subtitle_links"] == 1
    assert before_import_path.exists()

    assert _table_count(target_conn, "change_logs") >= 4
    name_row = target_conn.execute("SELECT raw_name FROM names").fetchone()
    assert name_row is not None
    assert name_row["raw_name"] == "Alice"


def test_import_csv_success_for_admin_on_empty_db(tmp_path: Path) -> None:
    source_db = _build_source_db(tmp_path / "source.sqlite3")
    export_service = ExportBackupService(source_db)
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    export_service.export_csv(csv_dir, role="admin")
    source_db.close()

    target_conn = initialize_database(tmp_path / "target.sqlite3")
    target_conn.row_factory = sqlite3.Row
    import_service = ImportService(target_conn)

    counts, before_import_path = import_service.import_csv(csv_dir, role="admin")
    assert before_import_path.exists()
    assert before_import_path.name.startswith("before_import_")
    assert counts["names"] == 1
    assert counts["titles"] == 1
    assert counts["subtitles"] == 1
    assert counts["name_subtitle_links"] == 1
    assert counts["change_logs"] >= 4
    assert before_import_path.exists()

    title_row = target_conn.execute("SELECT title_name FROM titles").fetchone()
    assert title_row is not None
    assert title_row["title_name"] == "Title-A"


def test_import_csv_preview_reports_counts_and_unknown_files(tmp_path: Path) -> None:
    source_db = _build_source_db(tmp_path / "source.sqlite3")
    export_service = ExportBackupService(source_db)
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    export_service.export_csv(csv_dir, role="admin")
    source_db.close()
    (csv_dir / "extra.csv").write_text("id\n1\n", encoding="utf-8")

    target_conn = initialize_database(tmp_path / "target.sqlite3")
    preview = ImportService(target_conn).preview_csv_source(csv_dir)

    assert preview.source_type == "csv"
    assert preview.ready is True
    assert preview.table_counts["names"] == 1
    assert preview.table_counts["titles"] == 1
    assert preview.table_counts["subtitles"] == 1
    assert preview.unknown_tables == ("extra",)
    assert preview.missing_tables == ()
    assert preview.invalid_tables == ()


def test_import_csv_preview_reports_missing_required_files(tmp_path: Path) -> None:
    source_db = _build_source_db(tmp_path / "source.sqlite3")
    export_service = ExportBackupService(source_db)
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    export_service.export_csv(csv_dir, role="admin")
    source_db.close()
    (csv_dir / "names.csv").unlink()

    target_conn = initialize_database(tmp_path / "target.sqlite3")
    preview = ImportService(target_conn).preview_csv_source(csv_dir)

    assert preview.ready is False
    assert preview.missing_tables == ("names",)
    assert "names" not in preview.table_counts


def test_import_json_preview_reports_counts_unknown_and_invalid_tables(tmp_path: Path) -> None:
    payload = {table_name: [] for table_name in TABLES}
    payload["names"] = [{"id": 1, "raw_name": "Alice"}]
    payload["titles"] = [{"id": 1, "title_name": "Title-A"}]
    payload["subtitles"] = ["not-object"]
    payload["extra"] = []
    json_path = tmp_path / "preview.json"
    json_path.write_text(json.dumps(payload), encoding="utf-8")

    target_conn = initialize_database(tmp_path / "target.sqlite3")
    preview = ImportService(target_conn).preview_json_source(json_path)

    assert preview.source_type == "json"
    assert preview.ready is False
    assert preview.table_counts["names"] == 1
    assert preview.table_counts["titles"] == 1
    assert preview.table_counts["subtitles"] == 1
    assert preview.invalid_tables == ("subtitles",)
    assert preview.unknown_tables == ("extra",)
    assert preview.missing_tables == ()


def test_import_json_preview_reports_missing_tables(tmp_path: Path) -> None:
    json_path = tmp_path / "preview.json"
    json_path.write_text('{"names": []}', encoding="utf-8")

    target_conn = initialize_database(tmp_path / "target.sqlite3")
    preview = ImportService(target_conn).preview_json_source(json_path)

    assert preview.ready is False
    assert preview.missing_tables == (
        "titles",
        "subtitles",
        "name_subtitle_links",
        "name_title_links",
        "change_logs",
    )


def test_import_rejects_viewer_and_editor(tmp_path: Path) -> None:
    source_db = _build_source_db(tmp_path / "source.sqlite3")
    export_service = ExportBackupService(source_db)
    json_path = tmp_path / "export.json"
    export_service.export_json(json_path, role="admin")

    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    export_service.export_csv(csv_dir, role="admin")
    source_db.close()

    target_conn = initialize_database(tmp_path / "target.sqlite3")
    import_service = ImportService(target_conn)

    with pytest.raises(AuthorizationError):
        import_service.import_json(json_path, role="viewer")

    with pytest.raises(AuthorizationError):
        import_service.import_json(json_path, role="editor")

    with pytest.raises(AuthorizationError):
        import_service.import_csv(csv_dir, role="viewer")

    with pytest.raises(AuthorizationError):
        import_service.import_csv(csv_dir, role="editor")


def test_import_rejects_non_empty_db(tmp_path: Path) -> None:
    source_db = _build_source_db(tmp_path / "source.sqlite3")
    export_service = ExportBackupService(source_db)
    json_path = tmp_path / "export.json"
    export_service.export_json(json_path, role="admin")
    source_db.close()

    target_conn = initialize_database(tmp_path / "target.sqlite3")
    target_conn.row_factory = sqlite3.Row
    core = CoreService(target_conn)
    core.create_name(NameInput(raw_name="Existing"), operator_id="op-1")
    target_conn.commit()

    import_service = ImportService(target_conn)
    with pytest.raises(ValidationError):
        import_service.import_json(json_path, role="admin")


def test_import_rejects_missing_csv_file_and_invalid_paths(tmp_path: Path) -> None:
    source_db = _build_source_db(tmp_path / "source.sqlite3")
    export_service = ExportBackupService(source_db)
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    export_service.export_csv(csv_dir, role="admin")
    source_db.close()

    (csv_dir / "names.csv").unlink()

    target_conn = initialize_database(tmp_path / "target.sqlite3")
    import_service = ImportService(target_conn)

    with pytest.raises(ValidationError):
        import_service.import_csv(csv_dir, role="admin")

    with pytest.raises(ValidationError):
        import_service.import_csv(tmp_path / "no-such-dir", role="admin")


def test_import_rejects_invalid_json(tmp_path: Path) -> None:
    target_conn = initialize_database(tmp_path / "target.sqlite3")
    import_service = ImportService(target_conn)

    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{invalid", encoding="utf-8")
    with pytest.raises(ValidationError):
        import_service.import_json(bad_json, role="admin")

    missing_keys_json = tmp_path / "missing_keys.json"
    missing_keys_json.write_text('{"names": []}', encoding="utf-8")
    with pytest.raises(ValidationError):
        import_service.import_json(missing_keys_json, role="admin")

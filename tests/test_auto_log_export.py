"""Tests for automatic change log JSONL export."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.application.auto_log_export import AutoExportingCoreService
from app.application.core_services import NameInput
from app.infrastructure.db import apply_schema


def _service(log_path: Path, *, max_bytes: int = 1024 * 1024) -> tuple[sqlite3.Connection, AutoExportingCoreService]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    apply_schema(conn)
    return conn, AutoExportingCoreService(conn, log_path=log_path, max_bytes=max_bytes)


def test_auto_change_log_jsonl_export(tmp_path: Path) -> None:
    log_path = tmp_path / "change_logs.jsonl"
    conn, service = _service(log_path)

    name_id = service.create_name(NameInput(raw_name="Alice"), operator_id="op")
    service.update_name(name_id, NameInput(raw_name="Alice Updated"), operator_id="op")

    db_logs = conn.execute("SELECT COUNT(*) FROM change_logs").fetchone()[0]
    assert db_logs == 2

    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    second = json.loads(lines[1])
    assert first["entity_type"] == "names"
    assert first["action"] == "create"
    assert first["operator_id"] == "op"
    assert json.loads(first["after_json"])["raw_name"] == "Alice"
    assert second["action"] == "update"
    assert json.loads(second["before_json"])["raw_name"] == "Alice"
    assert json.loads(second["after_json"])["raw_name"] == "Alice Updated"


def test_auto_change_log_rotation(tmp_path: Path) -> None:
    log_path = tmp_path / "change_logs.jsonl"
    log_path.write_text("x" * 2048, encoding="utf-8")
    _, service = _service(log_path, max_bytes=1024)

    service.create_name(NameInput(raw_name="Alice"), operator_id="op")

    assert log_path.exists()
    assert "Alice" in log_path.read_text(encoding="utf-8")
    archived = [path for path in tmp_path.iterdir() if path.name.startswith("change_logs.")]
    assert archived


def test_auto_change_log_export_is_best_effort(tmp_path: Path) -> None:
    log_path = tmp_path / "log-dir"
    log_path.mkdir()
    conn, service = _service(log_path)

    service.create_name(NameInput(raw_name="Alice"), operator_id="op")

    assert conn.execute("SELECT COUNT(*) FROM change_logs").fetchone()[0] == 1

"""Tests for change_logs recording from core services."""

from __future__ import annotations

import json
import sqlite3

from app.application.core_services import CoreService, NameInput
from app.infrastructure.db import apply_schema


def _service() -> tuple[sqlite3.Connection, CoreService]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    apply_schema(conn)
    return conn, CoreService(conn)


def test_change_logs_capture_minimum_fields() -> None:
    conn, service = _service()

    name_id = service.create_name(NameInput(raw_name="Alice"), operator_id="operator-x")
    service.update_name(name_id, NameInput(raw_name="Alice Updated"), operator_id="operator-x")
    service.delete_name(name_id, operator_id="operator-x")

    logs = conn.execute(
        """
        SELECT entity_type, entity_id, action, operator_id, before_json, after_json
        FROM change_logs
        WHERE entity_type = 'names' AND entity_id = ?
        ORDER BY id
        """,
        (name_id,),
    ).fetchall()

    assert [row["action"] for row in logs] == ["create", "update", "delete"]
    assert all(row["operator_id"] == "operator-x" for row in logs)

    update_before = json.loads(logs[1]["before_json"])
    update_after = json.loads(logs[1]["after_json"])
    assert update_before["raw_name"] == "Alice"
    assert update_after["raw_name"] == "Alice Updated"

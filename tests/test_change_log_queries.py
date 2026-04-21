"""Tests for change_logs query filters."""

from __future__ import annotations

import sqlite3

from app.application.core_services import CoreService, NameInput
from app.application.query_services import QueryService
from app.infrastructure.db import apply_schema


def _services() -> tuple[sqlite3.Connection, CoreService, QueryService]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    apply_schema(conn)
    return conn, CoreService(conn), QueryService(conn)


def test_list_change_logs_filtering() -> None:
    _, core, query = _services()

    name_id = core.create_name(NameInput(raw_name="Alice"), operator_id="alice-op")
    core.update_name(name_id, NameInput(raw_name="Alice Updated"), operator_id="alice-op")
    core.delete_name(name_id, operator_id="alice-op")

    all_logs = query.list_change_logs()
    assert len(all_logs) == 3

    delete_logs = query.list_change_logs(action="delete")
    assert [row.action for row in delete_logs] == ["delete"]

    entity_logs = query.list_change_logs(entity_type="names")
    assert len(entity_logs) == 3

    operator_logs = query.list_change_logs(operator_id="alice-op")
    assert len(operator_logs) == 3

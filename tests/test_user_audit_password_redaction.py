"""Regression tests for password redaction in user audit logs."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

import pytest

from app.application.user_services import CreateUserInput, UserService
from app.domain.errors import AuthorizationError
from app.infrastructure.db import apply_schema

_PASSWORD_TOKENS = (
    "plain-secret",
    "password_hash",
    "password_salt",
    "password_algorithm",
    "password_iterations",
    "password",
)


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    apply_schema(connection)
    return connection


def _audit_payloads(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute(
        """
        SELECT before_json, after_json
        FROM user_audit_logs
        ORDER BY id
        """
    ).fetchall()
    payloads: list[str] = []
    for row in rows:
        for key in ("before_json", "after_json"):
            value = row[key]
            if value is not None:
                json.loads(str(value))
                payloads.append(str(value))
    return payloads


def _assert_no_password_material(payloads: list[str]) -> None:
    combined = "\n".join(payloads)
    for token in _PASSWORD_TOKENS:
        assert token not in combined


def test_user_audit_logs_do_not_store_password_material() -> None:
    connection = _connection()
    service = UserService(connection)

    service.create_user(
        CreateUserInput(
            operator_id="admin",
            password="plain-secret",
            role="admin",
            display_name="Administrator",
        ),
        actor_operator_id="bootstrap",
        actor_role="admin",
    )
    service.create_user(
        CreateUserInput(
            operator_id="editor",
            password="plain-secret",
            role="editor",
            display_name="Editor",
        ),
        actor_operator_id="admin",
        actor_role="admin",
    )
    service.authenticate_user("editor", "plain-secret")
    with pytest.raises(AuthorizationError):
        service.authenticate_user("editor", "wrong-secret")

    payloads = _audit_payloads(connection)
    assert payloads
    _assert_no_password_material(payloads)


def test_audit_json_contains_only_expected_user_snapshot_keys() -> None:
    connection = _connection()
    service = UserService(connection)

    service.create_user(
        CreateUserInput(
            operator_id="admin",
            password="plain-secret",
            role="admin",
        ),
        actor_operator_id="bootstrap",
        actor_role="admin",
    )
    payloads = _audit_payloads(connection)
    assert payloads

    allowed_keys = {
        "operator_id",
        "display_name",
        "role",
        "auth_provider",
        "windows_account_name",
        "windows_sid",
        "disabled_at",
        "failed_login_count",
        "locked_until",
        "last_login_at",
        "reason",
    }
    for payload in payloads:
        data: dict[str, Any] = json.loads(payload)
        assert set(data) <= allowed_keys

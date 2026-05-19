"""Regression tests for Windows authentication user handling."""

from __future__ import annotations

import sqlite3

import pytest

from app.application.user_services import CreateUserInput, UserService
from app.application.windows_identity import WindowsIdentity
from app.domain.errors import AuthorizationError
from app.infrastructure.db import apply_schema


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    apply_schema(connection)
    return connection


def test_windows_auth_auto_creates_unknown_user_as_viewer() -> None:
    connection = _connection()
    service = UserService(connection)
    identity = WindowsIdentity(
        account_name="DOMAIN\\naoki",
        display_name="naoki",
        sid="S-1-5-21-1000",
    )

    user = service.authenticate_windows_user(identity)

    assert user.operator_id == "windows:S-1-5-21-1000"
    assert user.display_name == "naoki"
    assert user.role == "viewer"
    assert user.auth_provider == "windows"
    assert user.windows_account_name == "DOMAIN\\naoki"
    assert user.windows_sid == "S-1-5-21-1000"
    assert user.last_login_at is not None

    rows = connection.execute(
        """
        SELECT action, after_json
        FROM user_audit_logs
        WHERE target_operator_id = ?
        ORDER BY id
        """,
        (user.operator_id,),
    ).fetchall()
    assert [row["action"] for row in rows] == ["user_create", "login_success"]
    assert "windows_auto_viewer" in rows[0]["after_json"]


def test_windows_auth_reuses_existing_sid_and_preserves_role() -> None:
    connection = _connection()
    service = UserService(connection)
    identity = WindowsIdentity(
        account_name="DOMAIN\\naoki",
        display_name="naoki",
        sid="S-1-5-21-1000",
    )

    created = service.authenticate_windows_user(identity)
    service.create_user(
        CreateUserInput(
            operator_id="admin",
            password="secret",
            role="admin",
        ),
        actor_operator_id="bootstrap",
        actor_role="admin",
    )
    service.change_user_role(
        created.operator_id,
        "editor",
        actor_operator_id="admin",
        actor_role="admin",
    )

    authenticated = service.authenticate_windows_user(identity)

    assert authenticated.operator_id == created.operator_id
    assert authenticated.role == "editor"
    assert authenticated.auth_provider == "windows"
    assert authenticated.failed_login_count == 0


def test_windows_auth_can_fallback_to_account_name_when_sid_absent() -> None:
    connection = _connection()
    service = UserService(connection)
    identity = WindowsIdentity(account_name="DOMAIN\\fallback", display_name="fallback")

    first = service.authenticate_windows_user(identity)
    second = service.authenticate_windows_user(identity)

    assert first.operator_id == "windows:DOMAIN\\fallback"
    assert second.operator_id == first.operator_id
    assert len(service.list_users(include_disabled=True)) == 1


def test_local_auth_is_not_allowed_for_windows_user() -> None:
    connection = _connection()
    service = UserService(connection)
    identity = WindowsIdentity(account_name="DOMAIN\\naoki", display_name="naoki")
    user = service.authenticate_windows_user(identity)

    with pytest.raises(AuthorizationError):
        service.authenticate_user(user.operator_id, "any-password")

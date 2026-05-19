"""Release UAT coverage for authentication and last-admin protection."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from app.application.user_services import CreateUserInput, UserService
from app.application.windows_identity import WindowsIdentity
from app.domain.errors import AuthorizationError, StateTransitionError, ValidationError
from app.infrastructure.db import initialize_database


def test_uat_local_auth_failure_paths_write_expected_audit(tmp_path: Path) -> None:
    connection = _connection(tmp_path)
    try:
        service = UserService(connection)
        _create_local_user(service, "admin", "admin")
        _create_local_user(service, "viewer", "viewer", actor="admin")
        _create_local_user(service, "editor", "editor", actor="admin")

        with pytest.raises(AuthorizationError):
            service.authenticate_user("missing", "secret")
        with pytest.raises(AuthorizationError):
            service.authenticate_user("viewer", "wrong")
        with pytest.raises(ValidationError):
            service.authenticate_user("viewer", "")

        service.disable_user("viewer", actor_operator_id="admin", actor_role="admin")
        with pytest.raises(AuthorizationError):
            service.authenticate_user("viewer", "secret")

        connection.execute(
            "UPDATE users SET locked_until = ? WHERE operator_id = ?",
            ("2999-12-31T23:59:59+00:00", "editor"),
        )
        connection.commit()
        with pytest.raises(AuthorizationError):
            service.authenticate_user("editor", "secret")

        viewer_row = connection.execute(
            "SELECT failed_login_count FROM users WHERE operator_id = ?",
            ("viewer",),
        ).fetchone()
        assert viewer_row is not None
        assert int(viewer_row["failed_login_count"]) == 1

        failure_reasons = _audit_after_reasons(connection, "login_failure")
        assert failure_reasons == [
            "not_found",
            "credential_mismatch",
            "disabled",
            "locked",
        ]
    finally:
        connection.close()


def test_uat_windows_auth_first_existing_disabled_and_local_block(tmp_path: Path) -> None:
    connection = _connection(tmp_path)
    try:
        service = UserService(connection)
        _create_local_user(service, "admin", "admin")
        identity = WindowsIdentity(
            account_name="DOMAIN\\naoki",
            display_name="naoki",
            sid="S-1-5-21-1000",
        )

        created = service.authenticate_windows_user(identity)

        assert created.operator_id == "windows:S-1-5-21-1000"
        assert created.role == "viewer"
        assert created.auth_provider == "windows"
        assert created.last_login_at is not None

        service.change_user_role(
            created.operator_id,
            "editor",
            actor_operator_id="admin",
            actor_role="admin",
        )
        existing = service.authenticate_windows_user(identity)
        assert existing.operator_id == created.operator_id
        assert existing.role == "editor"

        with pytest.raises(AuthorizationError):
            service.authenticate_user(created.operator_id, "secret")

        service.disable_user(created.operator_id, actor_operator_id="admin", actor_role="admin")
        with pytest.raises(AuthorizationError):
            service.authenticate_windows_user(identity)

        actions = _audit_actions(connection)
        assert actions.count("user_create") == 2
        assert "user_role_change" in actions
        assert "user_disable" in actions
        assert actions.count("login_success") == 2
        assert _audit_after_reasons(connection, "login_failure") == [
            "local_auth_not_allowed",
            "disabled",
        ]
    finally:
        connection.close()


def test_uat_last_active_admin_protection_allows_safe_admin_rotation(
    tmp_path: Path,
) -> None:
    connection = _connection(tmp_path)
    try:
        service = UserService(connection)
        _create_local_user(service, "admin1", "admin")

        with pytest.raises(StateTransitionError, match="last active admin"):
            service.change_user_role(
                "admin1",
                "editor",
                actor_operator_id="admin1",
                actor_role="admin",
            )
        with pytest.raises(StateTransitionError, match="last active admin"):
            service.disable_user("admin1", actor_operator_id="admin1", actor_role="admin")

        _create_local_user(service, "admin2", "admin", actor="admin1")
        service.change_user_role(
            "admin2",
            "editor",
            actor_operator_id="admin1",
            actor_role="admin",
        )

        assert service.get_user("admin2").role == "editor"
        assert _active_admin_count(connection) == 1

        with pytest.raises(StateTransitionError, match="last active admin"):
            service.change_user_role(
                "admin1",
                "viewer",
                actor_operator_id="admin1",
                actor_role="admin",
            )
        with pytest.raises(StateTransitionError, match="last active admin"):
            service.disable_user("admin1", actor_operator_id="admin1", actor_role="admin")

        assert service.get_user("admin1").role == "admin"
        assert service.get_user("admin1").disabled_at is None
    finally:
        connection.close()


def _connection(tmp_path: Path) -> sqlite3.Connection:
    return initialize_database(tmp_path / "nameverification.db")


def _create_local_user(
    service: UserService,
    operator_id: str,
    role: str,
    *,
    actor: str = "system",
) -> None:
    service.create_user(
        CreateUserInput(operator_id=operator_id, role=role, password="secret"),
        actor_operator_id=actor,
        actor_role="admin",
    )


def _audit_actions(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute(
        "SELECT action FROM user_audit_logs ORDER BY id",
    ).fetchall()
    return [str(row["action"]) for row in rows]


def _audit_after_reasons(connection: sqlite3.Connection, action: str) -> list[str]:
    rows = connection.execute(
        """
        SELECT after_json
        FROM user_audit_logs
        WHERE action = ?
        ORDER BY id
        """,
        (action,),
    ).fetchall()
    reasons: list[str] = []
    for row in rows:
        payload = _json_object(row["after_json"])
        reason = payload.get("reason")
        if isinstance(reason, str):
            reasons.append(reason)
    return reasons


def _active_admin_count(connection: sqlite3.Connection) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS count FROM users WHERE role = 'admin' AND disabled_at IS NULL"
    ).fetchone()
    assert row is not None
    return int(row["count"])


def _json_object(value: Any) -> dict[str, Any]:
    assert isinstance(value, str)
    payload = json.loads(value)
    assert isinstance(payload, dict)
    return payload

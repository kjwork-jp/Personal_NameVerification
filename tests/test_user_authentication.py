from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.application.user_services import CreateUserInput, UserService
from app.domain.errors import AuthorizationError, ValidationError
from app.infrastructure.db import initialize_database


def test_authenticate_user_returns_role_and_resets_failed_count(tmp_path: Path) -> None:
    connection = _connection(tmp_path)
    try:
        service = UserService(connection)
        service.create_user(
            CreateUserInput(operator_id="editor", role="editor", password="secret"),
            actor_operator_id="system",
            actor_role="admin",
        )
        connection.execute(
            "UPDATE users SET failed_login_count = 2 WHERE operator_id = ?",
            ("editor",),
        )
        connection.commit()

        user = service.authenticate_user("editor", "secret")

        assert user.operator_id == "editor"
        assert user.role == "editor"
        assert user.failed_login_count == 0
        assert user.last_login_at is not None
        assert _audit_count(connection, "login_success") == 1
    finally:
        connection.close()


def test_authenticate_user_rejects_wrong_password_and_increments_failure(
    tmp_path: Path,
) -> None:
    connection = _connection(tmp_path)
    try:
        service = UserService(connection)
        service.create_user(
            CreateUserInput(operator_id="viewer", role="viewer", password="secret"),
            actor_operator_id="system",
            actor_role="admin",
        )

        with pytest.raises(AuthorizationError):
            service.authenticate_user("viewer", "wrong")

        row = connection.execute(
            "SELECT failed_login_count FROM users WHERE operator_id = ?",
            ("viewer",),
        ).fetchone()
        assert row[0] == 1
        assert _audit_count(connection, "login_failure") == 1
    finally:
        connection.close()


def test_authenticate_user_rejects_unknown_operator(tmp_path: Path) -> None:
    connection = _connection(tmp_path)
    try:
        service = UserService(connection)

        with pytest.raises(AuthorizationError):
            service.authenticate_user("missing", "secret")

        assert _audit_count(connection, "login_failure") == 1
    finally:
        connection.close()


def test_authenticate_user_rejects_disabled_user(tmp_path: Path) -> None:
    connection = _connection(tmp_path)
    try:
        service = UserService(connection)
        service.create_user(
            CreateUserInput(operator_id="admin", role="admin", password="secret"),
            actor_operator_id="system",
            actor_role="admin",
        )
        service.create_user(
            CreateUserInput(operator_id="viewer", role="viewer", password="secret"),
            actor_operator_id="admin",
            actor_role="admin",
        )
        service.disable_user("viewer", actor_operator_id="admin", actor_role="admin")

        with pytest.raises(AuthorizationError):
            service.authenticate_user("viewer", "secret")

        assert _audit_count(connection, "login_failure") == 1
    finally:
        connection.close()


def test_authenticate_user_rejects_blank_password(tmp_path: Path) -> None:
    connection = _connection(tmp_path)
    try:
        service = UserService(connection)

        with pytest.raises(ValidationError):
            service.authenticate_user("viewer", "")
    finally:
        connection.close()


def _connection(tmp_path: Path) -> sqlite3.Connection:
    return initialize_database(tmp_path / "nameverification.db")


def _audit_count(connection: sqlite3.Connection, action: str) -> int:
    row = connection.execute(
        "SELECT COUNT(*) FROM user_audit_logs WHERE action = ?",
        (action,),
    ).fetchone()
    return int(row[0])

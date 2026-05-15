from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.application.user_services import CreateUserInput, UserService
from app.domain.errors import AuthorizationError, ConflictError, NotFoundError, StateTransitionError, ValidationError
from app.infrastructure.db import initialize_database


def test_create_user_hashes_password_and_writes_audit(tmp_path: Path) -> None:
    connection = _connection(tmp_path)
    try:
        service = UserService(connection)

        user_id = service.create_user(
            CreateUserInput(
                operator_id="admin",
                display_name="Admin User",
                role="admin",
                password="admin-password",
            ),
            actor_operator_id="system",
            actor_role="admin",
        )

        row = connection.execute(
            "SELECT operator_id, display_name, role, password_hash, password_salt, password_algorithm, password_iterations FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        assert row is not None
        assert row["operator_id"] == "admin"
        assert row["display_name"] == "Admin User"
        assert row["role"] == "admin"
        assert row["password_hash"] != "admin-password"
        assert row["password_salt"]
        assert row["password_algorithm"] == "pbkdf2_sha256"
        assert row["password_iterations"] >= 310_000
        assert _audit_count(connection, "user_create") == 1
    finally:
        connection.close()


def test_create_user_requires_admin_role(tmp_path: Path) -> None:
    connection = _connection(tmp_path)
    try:
        service = UserService(connection)

        with pytest.raises(AuthorizationError):
            service.create_user(
                CreateUserInput(operator_id="viewer", role="viewer", password="secret"),
                actor_operator_id="admin",
                actor_role="editor",
            )
    finally:
        connection.close()


def test_create_user_rejects_blank_operator_id(tmp_path: Path) -> None:
    connection = _connection(tmp_path)
    try:
        service = UserService(connection)

        with pytest.raises(ValidationError):
            service.create_user(
                CreateUserInput(operator_id=" ", role="viewer", password="secret"),
                actor_operator_id="admin",
                actor_role="admin",
            )
    finally:
        connection.close()


def test_create_user_rejects_duplicate_operator_id(tmp_path: Path) -> None:
    connection = _connection(tmp_path)
    try:
        service = UserService(connection)
        payload = CreateUserInput(operator_id="admin", role="admin", password="secret")
        service.create_user(payload, actor_operator_id="system", actor_role="admin")

        with pytest.raises(ConflictError):
            service.create_user(payload, actor_operator_id="system", actor_role="admin")
    finally:
        connection.close()


def test_change_user_role_updates_role_and_writes_audit(tmp_path: Path) -> None:
    connection = _connection(tmp_path)
    try:
        service = UserService(connection)
        service.create_user(
            CreateUserInput(operator_id="admin", role="admin", password="secret"),
            actor_operator_id="system",
            actor_role="admin",
        )
        service.create_user(
            CreateUserInput(operator_id="editor", role="editor", password="secret"),
            actor_operator_id="admin",
            actor_role="admin",
        )

        service.change_user_role(
            "editor",
            "viewer",
            actor_operator_id="admin",
            actor_role="admin",
        )

        assert service.get_user("editor").role == "viewer"
        assert _audit_count(connection, "user_role_change") == 1
    finally:
        connection.close()


def test_change_user_role_prevents_last_active_admin_demotion(tmp_path: Path) -> None:
    connection = _connection(tmp_path)
    try:
        service = UserService(connection)
        service.create_user(
            CreateUserInput(operator_id="admin", role="admin", password="secret"),
            actor_operator_id="system",
            actor_role="admin",
        )

        with pytest.raises(StateTransitionError, match="last active admin"):
            service.change_user_role(
                "admin",
                "editor",
                actor_operator_id="admin",
                actor_role="admin",
            )
    finally:
        connection.close()


def test_disable_user_prevents_last_active_admin_disable(tmp_path: Path) -> None:
    connection = _connection(tmp_path)
    try:
        service = UserService(connection)
        service.create_user(
            CreateUserInput(operator_id="admin", role="admin", password="secret"),
            actor_operator_id="system",
            actor_role="admin",
        )

        with pytest.raises(StateTransitionError, match="last active admin"):
            service.disable_user("admin", actor_operator_id="admin", actor_role="admin")
    finally:
        connection.close()


def test_disable_and_enable_user(tmp_path: Path) -> None:
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

        with pytest.raises(NotFoundError):
            service.get_user("viewer")
        assert service.get_user("viewer", include_disabled=True).disabled_at is not None
        assert _audit_count(connection, "user_disable") == 1

        service.enable_user("viewer", actor_operator_id="admin", actor_role="admin")

        assert service.get_user("viewer").disabled_at is None
        assert _audit_count(connection, "user_enable") == 1
    finally:
        connection.close()


def test_list_users_can_exclude_disabled_users(tmp_path: Path) -> None:
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

        active_users = service.list_users(include_disabled=False)

        assert [user.operator_id for user in active_users] == ["admin"]
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

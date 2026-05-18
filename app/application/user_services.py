"""User management services for local and Windows authentication."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal, TypeVar, cast

from app.application.authorization import ServiceRole, require_admin, require_known_role
from app.application.password_services import PasswordHash, hash_password, verify_password
from app.application.windows_identity import WindowsIdentity
from app.domain.errors import (
    AuthorizationError,
    ConflictError,
    NotFoundError,
    StateTransitionError,
    ValidationError,
)

R = TypeVar("R")
AuthProvider = Literal["local", "windows"]
_WINDOWS_DISABLED_PASSWORD = "__windows_auth_password_disabled__"


@dataclass(frozen=True, slots=True)
class CreateUserInput:
    operator_id: str
    password: str
    role: ServiceRole
    display_name: str | None = None


@dataclass(frozen=True, slots=True)
class UserRecord:
    id: int
    public_id: str | None
    operator_id: str
    display_name: str | None
    role: ServiceRole
    auth_provider: AuthProvider
    windows_account_name: str | None
    windows_sid: str | None
    disabled_at: str | None
    failed_login_count: int
    locked_until: str | None
    last_login_at: str | None
    created_at: str
    updated_at: str


class UserService:
    """Application service for admin-managed local and Windows users."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute("PRAGMA foreign_keys = ON;")

    def create_user(
        self,
        payload: CreateUserInput,
        *,
        actor_operator_id: str,
        actor_role: ServiceRole = "admin",
    ) -> int:
        """Create a local password user. Only admin can create users."""

        def operation() -> int:
            require_admin(actor_role, action="create_user")
            self._validate_operator_id(actor_operator_id, field_name="actor_operator_id")
            self._validate_operator_id(payload.operator_id, field_name="operator_id")
            if payload.password == "":
                raise ValidationError("password is required")
            role = require_known_role(payload.role, action="create_user")
            stored = hash_password(payload.password)
            now = _utc_now()
            try:
                cursor = self._connection.execute(
                    """
                    INSERT INTO users(
                        operator_id,
                        display_name,
                        role,
                        auth_provider,
                        password_hash,
                        password_salt,
                        password_algorithm,
                        password_iterations,
                        password_updated_at,
                        created_at,
                        updated_at
                    ) VALUES (?, ?, ?, 'local', ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        payload.operator_id,
                        payload.display_name,
                        role,
                        stored.password_hash,
                        stored.salt,
                        stored.algorithm,
                        stored.iterations,
                        now,
                        now,
                        now,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise ConflictError("operator_id already exists") from exc

            user_id = _require_lastrowid(cursor)
            created = self.get_user(payload.operator_id, include_disabled=True)
            self._insert_user_audit_log(
                actor_operator_id=actor_operator_id,
                target_operator_id=payload.operator_id,
                action="user_create",
                before=None,
                after=_audit_user_record(created),
            )
            return user_id

        return self._write(operation)

    def authenticate_user(self, operator_id: str, password: str) -> UserRecord:
        """Authenticate a local password user."""

        self._validate_operator_id(operator_id, field_name="operator_id")
        if password == "":
            raise ValidationError("password is required")

        row = self._get_user_row_with_password(operator_id)
        if row is None:
            self._insert_user_audit_log(
                actor_operator_id=operator_id,
                target_operator_id=operator_id,
                action="login_failure",
                before=None,
                after={
                    "operator_id": operator_id,
                    "auth_provider": "local",
                    "reason": "not_found",
                },
            )
            self._connection.commit()
            raise AuthorizationError("invalid operator_id or password")

        user = _user_record_from_row(row)
        if user.auth_provider != "local":
            self._insert_login_failure(user, reason="local_auth_not_allowed")
            self._connection.commit()
            raise AuthorizationError("local password login is not available for this user")
        self._ensure_login_allowed(user)
        now = _utc_now()

        if not verify_password(password, _password_hash_from_row(row)):
            self._connection.execute(
                """
                UPDATE users
                SET failed_login_count = failed_login_count + 1, updated_at = ?
                WHERE id = ?
                """,
                (now, user.id),
            )
            after_failure = self.get_user(operator_id, include_disabled=True)
            self._insert_user_audit_log(
                actor_operator_id=operator_id,
                target_operator_id=operator_id,
                action="login_failure",
                before=_audit_user_record(user),
                after={**_audit_user_record(after_failure), "reason": "credential_mismatch"},
            )
            self._connection.commit()
            raise AuthorizationError("invalid operator_id or password")

        return self._mark_login_success(user)

    def authenticate_windows_user(self, identity: WindowsIdentity) -> UserRecord:
        """Authenticate current Windows session and auto-create unknown users as viewer."""

        if identity.account_name.strip() == "":
            raise ValidationError("windows account name is required")
        row = self._find_windows_user_row(identity)
        if row is None:
            return self._create_windows_viewer(identity)
        user = _user_record_from_row(row)
        self._ensure_login_allowed(user)
        return self._mark_login_success(user)

    def change_user_role(
        self,
        operator_id: str,
        new_role: ServiceRole,
        *,
        actor_operator_id: str,
        actor_role: ServiceRole = "admin",
    ) -> None:
        """Change a user's role while preserving at least one active admin."""

        def operation() -> None:
            require_admin(actor_role, action="change_user_role")
            self._validate_operator_id(actor_operator_id, field_name="actor_operator_id")
            self._validate_operator_id(operator_id, field_name="operator_id")
            role = require_known_role(new_role, action="change_user_role")
            before = self.get_user(operator_id, include_disabled=True)
            if before.role == "admin" and role != "admin" and self._active_admin_count() <= 1:
                raise StateTransitionError("cannot demote the last active admin")

            now = _utc_now()
            self._connection.execute(
                "UPDATE users SET role = ?, updated_at = ? WHERE operator_id = ?",
                (role, now, operator_id),
            )
            after = self.get_user(operator_id, include_disabled=True)
            self._insert_user_audit_log(
                actor_operator_id=actor_operator_id,
                target_operator_id=operator_id,
                action="user_role_change",
                before=_audit_user_record(before),
                after=_audit_user_record(after),
            )

        self._write(operation)

    def disable_user(
        self,
        operator_id: str,
        *,
        actor_operator_id: str,
        actor_role: ServiceRole = "admin",
    ) -> None:
        """Disable a user while preserving at least one active admin."""

        def operation() -> None:
            require_admin(actor_role, action="disable_user")
            self._validate_operator_id(actor_operator_id, field_name="actor_operator_id")
            self._validate_operator_id(operator_id, field_name="operator_id")
            before = self.get_user(operator_id, include_disabled=True)
            if before.disabled_at is not None:
                return
            if before.role == "admin" and self._active_admin_count() <= 1:
                raise StateTransitionError("cannot disable the last active admin")

            now = _utc_now()
            self._connection.execute(
                "UPDATE users SET disabled_at = ?, updated_at = ? WHERE operator_id = ?",
                (now, now, operator_id),
            )
            after = self.get_user(operator_id, include_disabled=True)
            self._insert_user_audit_log(
                actor_operator_id=actor_operator_id,
                target_operator_id=operator_id,
                action="user_disable",
                before=_audit_user_record(before),
                after=_audit_user_record(after),
            )

        self._write(operation)

    def enable_user(
        self,
        operator_id: str,
        *,
        actor_operator_id: str,
        actor_role: ServiceRole = "admin",
    ) -> None:
        """Enable a disabled user."""

        def operation() -> None:
            require_admin(actor_role, action="enable_user")
            self._validate_operator_id(actor_operator_id, field_name="actor_operator_id")
            self._validate_operator_id(operator_id, field_name="operator_id")
            before = self.get_user(operator_id, include_disabled=True)
            if before.disabled_at is None:
                return

            now = _utc_now()
            self._connection.execute(
                "UPDATE users SET disabled_at = NULL, updated_at = ? WHERE operator_id = ?",
                (now, operator_id),
            )
            after = self.get_user(operator_id, include_disabled=True)
            self._insert_user_audit_log(
                actor_operator_id=actor_operator_id,
                target_operator_id=operator_id,
                action="user_enable",
                before=_audit_user_record(before),
                after=_audit_user_record(after),
            )

        self._write(operation)

    def get_user(self, operator_id: str, *, include_disabled: bool = False) -> UserRecord:
        """Return a user by operator_id."""

        self._validate_operator_id(operator_id, field_name="operator_id")
        where = "operator_id = ?" if include_disabled else "operator_id = ? AND disabled_at IS NULL"
        row = self._connection.execute(
            f"""
            SELECT
                id,
                public_id,
                operator_id,
                display_name,
                role,
                auth_provider,
                windows_account_name,
                windows_sid,
                disabled_at,
                failed_login_count,
                locked_until,
                last_login_at,
                created_at,
                updated_at
            FROM users
            WHERE {where}
            """,
            (operator_id,),
        ).fetchone()
        if row is None:
            raise NotFoundError("user not found")
        return _user_record_from_row(row)

    def list_users(self, *, include_disabled: bool = True) -> list[UserRecord]:
        """Return users ordered by operator_id."""

        where = "" if include_disabled else "WHERE disabled_at IS NULL"
        rows = self._connection.execute(
            f"""
            SELECT
                id,
                public_id,
                operator_id,
                display_name,
                role,
                auth_provider,
                windows_account_name,
                windows_sid,
                disabled_at,
                failed_login_count,
                locked_until,
                last_login_at,
                created_at,
                updated_at
            FROM users
            {where}
            ORDER BY operator_id
            """
        ).fetchall()
        return [_user_record_from_row(row) for row in rows]

    def _create_windows_viewer(self, identity: WindowsIdentity) -> UserRecord:
        def operation() -> UserRecord:
            stored = hash_password(_WINDOWS_DISABLED_PASSWORD)
            now = _utc_now()
            operator_id = _windows_operator_id(identity)
            try:
                self._connection.execute(
                    """
                    INSERT INTO users(
                        operator_id,
                        display_name,
                        role,
                        auth_provider,
                        windows_account_name,
                        windows_sid,
                        password_hash,
                        password_salt,
                        password_algorithm,
                        password_iterations,
                        password_updated_at,
                        last_login_at,
                        created_at,
                        updated_at
                    ) VALUES (?, ?, 'viewer', 'windows', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        operator_id,
                        identity.display_name,
                        identity.account_name,
                        identity.sid,
                        stored.password_hash,
                        stored.salt,
                        stored.algorithm,
                        stored.iterations,
                        now,
                        now,
                        now,
                        now,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise ConflictError("windows user already exists") from exc
            created = self.get_user(operator_id, include_disabled=True)
            self._insert_user_audit_log(
                actor_operator_id=operator_id,
                target_operator_id=operator_id,
                action="user_create",
                before=None,
                after={**_audit_user_record(created), "reason": "windows_auto_viewer"},
            )
            self._insert_user_audit_log(
                actor_operator_id=operator_id,
                target_operator_id=operator_id,
                action="login_success",
                before=None,
                after=_audit_user_record(created),
            )
            return created

        return self._write(operation)

    def _mark_login_success(self, user: UserRecord) -> UserRecord:
        def operation() -> UserRecord:
            now = _utc_now()
            self._connection.execute(
                """
                UPDATE users
                SET failed_login_count = 0, last_login_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (now, now, user.id),
            )
            authenticated = self.get_user(user.operator_id, include_disabled=True)
            self._insert_user_audit_log(
                actor_operator_id=user.operator_id,
                target_operator_id=user.operator_id,
                action="login_success",
                before=_audit_user_record(user),
                after=_audit_user_record(authenticated),
            )
            return authenticated

        return self._write(operation)

    def _find_windows_user_row(self, identity: WindowsIdentity) -> sqlite3.Row | None:
        if identity.sid:
            row = self._connection.execute(
                """
                SELECT * FROM users
                WHERE auth_provider = 'windows' AND windows_sid = ?
                """,
                (identity.sid,),
            ).fetchone()
            if row is not None:
                return cast(sqlite3.Row, row)
        row = self._connection.execute(
            """
            SELECT * FROM users
            WHERE auth_provider = 'windows' AND windows_account_name = ?
            """,
            (identity.account_name,),
        ).fetchone()
        return cast(sqlite3.Row | None, row)

    def _active_admin_count(self) -> int:
        row = self._connection.execute(
            "SELECT COUNT(*) FROM users WHERE role = 'admin' AND disabled_at IS NULL"
        ).fetchone()
        return int(_row_value(row, "COUNT(*)", 0))

    def _get_user_row_with_password(self, operator_id: str) -> sqlite3.Row | None:
        row = self._connection.execute(
            """
            SELECT
                id,
                public_id,
                operator_id,
                display_name,
                role,
                auth_provider,
                windows_account_name,
                windows_sid,
                disabled_at,
                failed_login_count,
                locked_until,
                last_login_at,
                created_at,
                updated_at,
                password_hash,
                password_salt,
                password_algorithm,
                password_iterations
            FROM users
            WHERE operator_id = ?
            """,
            (operator_id,),
        ).fetchone()
        return cast(sqlite3.Row | None, row)

    def _ensure_login_allowed(self, user: UserRecord) -> None:
        if user.disabled_at is not None:
            self._insert_login_failure(user, reason="disabled")
            self._connection.commit()
            raise AuthorizationError("user is disabled")
        now = _utc_now()
        if user.locked_until is not None and user.locked_until > now:
            self._insert_login_failure(user, reason="locked")
            self._connection.commit()
            raise AuthorizationError("user is locked")

    def _insert_login_failure(self, user: UserRecord, *, reason: str) -> None:
        self._insert_user_audit_log(
            actor_operator_id=user.operator_id,
            target_operator_id=user.operator_id,
            action="login_failure",
            before=_audit_user_record(user),
            after={**_audit_user_record(user), "reason": reason},
        )

    def _insert_user_audit_log(
        self,
        *,
        actor_operator_id: str,
        target_operator_id: str,
        action: str,
        before: dict[str, Any] | None,
        after: dict[str, Any] | None,
    ) -> None:
        self._connection.execute(
            """
            INSERT INTO user_audit_logs(
                actor_operator_id, target_operator_id, action, before_json, after_json
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                actor_operator_id,
                target_operator_id,
                action,
                _json_or_none(before),
                _json_or_none(after),
            ),
        )

    def _write(self, operation: Callable[[], R]) -> R:
        try:
            result = operation()
            self._connection.commit()
            return result
        except Exception:
            self._connection.rollback()
            raise

    @staticmethod
    def _validate_operator_id(value: str, *, field_name: str) -> None:
        if value.strip() == "":
            raise ValidationError(f"{field_name} is required")


def _user_record_from_row(row: Any) -> UserRecord:
    return UserRecord(
        id=int(_row_value(row, "id", 0)),
        public_id=_optional_str(_row_value(row, "public_id", 1)),
        operator_id=str(_row_value(row, "operator_id", 2)),
        display_name=_optional_str(_row_value(row, "display_name", 3)),
        role=require_known_role(str(_row_value(row, "role", 4)), action="read_user"),
        auth_provider=_auth_provider(str(_row_value(row, "auth_provider", 5))),
        windows_account_name=_optional_str(_row_value(row, "windows_account_name", 6)),
        windows_sid=_optional_str(_row_value(row, "windows_sid", 7)),
        disabled_at=_optional_str(_row_value(row, "disabled_at", 8)),
        failed_login_count=int(_row_value(row, "failed_login_count", 9)),
        locked_until=_optional_str(_row_value(row, "locked_until", 10)),
        last_login_at=_optional_str(_row_value(row, "last_login_at", 11)),
        created_at=str(_row_value(row, "created_at", 12)),
        updated_at=str(_row_value(row, "updated_at", 13)),
    )


def _password_hash_from_row(row: Any) -> PasswordHash:
    return PasswordHash(
        algorithm=str(_row_value(row, "password_algorithm", 16)),
        iterations=int(_row_value(row, "password_iterations", 17)),
        salt=str(_row_value(row, "password_salt", 15)),
        password_hash=str(_row_value(row, "password_hash", 14)),
    )


def _audit_user_record(user: UserRecord) -> dict[str, Any]:
    return {
        "operator_id": user.operator_id,
        "display_name": user.display_name,
        "role": user.role,
        "auth_provider": user.auth_provider,
        "windows_account_name": user.windows_account_name,
        "windows_sid": user.windows_sid,
        "disabled_at": user.disabled_at,
        "failed_login_count": user.failed_login_count,
        "locked_until": user.locked_until,
        "last_login_at": user.last_login_at,
    }


def _windows_operator_id(identity: WindowsIdentity) -> str:
    source = identity.sid or identity.account_name
    return f"windows:{source}"


def _auth_provider(value: str) -> AuthProvider:
    if value in {"local", "windows"}:
        return cast(AuthProvider, value)
    return "local"


def _json_or_none(value: dict[str, Any] | None) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _row_value(row: Any, key: str, index: int) -> Any:
    try:
        return row[key]
    except (TypeError, IndexError):
        return row[index]


def _require_lastrowid(cursor: sqlite3.Cursor) -> int:
    if cursor.lastrowid is None:
        raise RuntimeError("SQLite did not return lastrowid")
    return int(cursor.lastrowid)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")

"""Read service for authentication and user-management audit logs."""

from __future__ import annotations

import sqlite3
from typing import Any

from app.application.authorization import ServiceRole, require_admin
from app.application.read_models import UserAuditLogRow


class UserAuditLogService:
    """Read-only service for user_audit_logs."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def list_user_audit_logs(
        self,
        role: ServiceRole = "admin",
        *,
        actor_operator_id: str | None = None,
        target_operator_id: str | None = None,
        action: str | None = None,
        limit: int = 200,
    ) -> list[UserAuditLogRow]:
        """Return user audit log rows. Admin only."""

        require_admin(role, action="list_user_audit_logs")
        clauses: list[str] = []
        params: list[Any] = []
        if actor_operator_id:
            clauses.append("actor_operator_id LIKE ?")
            params.append(f"%{actor_operator_id}%")
        if target_operator_id:
            clauses.append("target_operator_id LIKE ?")
            params.append(f"%{target_operator_id}%")
        if action:
            clauses.append("action = ?")
            params.append(action)
        where_sql = ""
        if clauses:
            where_sql = "WHERE " + " AND ".join(clauses)
        params.append(limit)
        rows = self._connection.execute(
            f"""
            SELECT
                id,
                actor_operator_id,
                target_operator_id,
                action,
                before_json,
                after_json,
                created_at
            FROM user_audit_logs
            {where_sql}
            ORDER BY id DESC
            LIMIT ?
            """,
            params,
        ).fetchall()
        return [_row_to_user_audit_log(row) for row in rows]


def _row_to_user_audit_log(row: Any) -> UserAuditLogRow:
    return UserAuditLogRow(
        id=int(_row_value(row, "id", 0)),
        actor_operator_id=str(_row_value(row, "actor_operator_id", 1)),
        target_operator_id=_optional_str(_row_value(row, "target_operator_id", 2)),
        action=str(_row_value(row, "action", 3)),
        before_json=_optional_str(_row_value(row, "before_json", 4)),
        after_json=_optional_str(_row_value(row, "after_json", 5)),
        created_at=str(_row_value(row, "created_at", 6)),
    )


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _row_value(row: Any, key: str, index: int) -> Any:
    try:
        return row[key]
    except (TypeError, IndexError):
        return row[index]

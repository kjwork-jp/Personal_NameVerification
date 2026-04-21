"""Minimal service-layer authorization helpers."""

from __future__ import annotations

from typing import Literal, cast

from app.domain.errors import AuthorizationError

ServiceRole = Literal["viewer", "editor", "admin"]


def require_editor_or_admin(role: ServiceRole, *, action: str) -> None:
    if role not in {"editor", "admin"}:
        raise AuthorizationError(f"role={role} is not allowed to {action}")


def require_admin(role: ServiceRole, *, action: str) -> None:
    if role != "admin":
        raise AuthorizationError(f"role={role} is not allowed to {action}")


def require_known_role(role: str, *, action: str) -> ServiceRole:
    if role not in {"viewer", "editor", "admin"}:
        raise AuthorizationError(f"role={role} is not allowed to {action}")
    return cast(ServiceRole, role)

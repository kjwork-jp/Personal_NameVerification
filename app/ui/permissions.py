"""Permission helpers for minimal UI-level RBAC."""

from __future__ import annotations

from app.ui.role_context import UserRole


def can_create_or_update(role: UserRole) -> bool:
    return role in {"editor", "admin"}


def can_run_destructive_actions(role: UserRole) -> bool:
    return role == "admin"


def can_link(role: UserRole) -> bool:
    return role in {"editor", "admin"}


def can_unlink(role: UserRole) -> bool:
    return role == "admin"

"""UI role context for minimal local RBAC guards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

UserRole = Literal["viewer", "editor", "admin"]
AuthProvider = Literal["local", "windows"]


@dataclass(frozen=True)
class RoleContext:
    role: UserRole = "admin"
    operator_id: str = "local-admin"
    auth_provider: AuthProvider = "local"

    @classmethod
    def admin(cls) -> RoleContext:
        return cls(role="admin", operator_id="local-admin", auth_provider="local")

"""UI role context for minimal local RBAC guards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

UserRole = Literal["viewer", "editor", "admin"]


@dataclass(frozen=True)
class RoleContext:
    role: UserRole = "admin"
    operator_id: str = "local-admin"

    @classmethod
    def admin(cls) -> RoleContext:
        return cls(role="admin", operator_id="local-admin")

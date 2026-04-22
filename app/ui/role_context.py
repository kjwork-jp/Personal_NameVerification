"""UI role context for minimal RBAC guards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

UserRole = Literal["viewer", "editor", "admin"]


@dataclass(frozen=True)
class RoleContext:
    role: UserRole = "admin"

    @classmethod
    def admin(cls) -> RoleContext:
        return cls(role="admin")

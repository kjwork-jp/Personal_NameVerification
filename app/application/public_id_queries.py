"""Read-only public_id lookup helpers."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Literal

from app.application.authorization import ServiceRole, require_known_role
from app.domain.errors import NotFoundError, ValidationError

PublicIdTable = Literal[
    "names",
    "titles",
    "subtitles",
    "name_subtitle_links",
    "name_title_links",
    "change_logs",
]

_PUBLIC_ID_TABLES: frozenset[str] = frozenset(
    {
        "names",
        "titles",
        "subtitles",
        "name_subtitle_links",
        "name_title_links",
        "change_logs",
    }
)


@dataclass(frozen=True)
class PublicIdLookupResult:
    """Minimal mapping between public_id and internal integer id."""

    table_name: str
    public_id: str
    internal_id: int


class PublicIdQueryService:
    """Read-only helper for resolving external public IDs."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute("PRAGMA foreign_keys = ON;")

    def resolve_internal_id(
        self,
        table_name: PublicIdTable,
        public_id: str,
        role: ServiceRole = "admin",
    ) -> PublicIdLookupResult:
        """Resolve a public_id into the current database internal integer id."""

        require_known_role(role, action="resolve_internal_id")
        _validate_public_id_lookup_table(table_name)
        normalized_public_id = public_id.strip()
        if not normalized_public_id:
            raise ValidationError("public_id must not be empty")

        row = self._connection.execute(
            f"SELECT id, public_id FROM {table_name} WHERE public_id = ?",
            (normalized_public_id,),
        ).fetchone()
        if row is None:
            raise NotFoundError(f"{table_name}(public_id={normalized_public_id}) not found")

        return PublicIdLookupResult(
            table_name=table_name,
            public_id=str(row["public_id"]),
            internal_id=int(row["id"]),
        )


def _validate_public_id_lookup_table(table_name: str) -> None:
    if table_name not in _PUBLIC_ID_TABLES:
        raise ValidationError(f"public_id lookup table is not allowed: {table_name}")

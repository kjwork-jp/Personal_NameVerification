"""Query/read-only services for search and listings."""

from __future__ import annotations

import sqlite3
from typing import Any

from app.application.authorization import ServiceRole, require_known_role
from app.application.read_models import (
    ChangeLogRow,
    NameDetail,
    NameSearchRow,
    NameTitleLinkRow,
    RelatedRow,
    SubtitleDetail,
    TitleDetail,
)
from app.domain.errors import NotFoundError
from app.domain.normalization import normalize_with_raw


class QueryService:
    """Read-only query service."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute("PRAGMA foreign_keys = ON;")

    def search_names(
        self,
        query: str | None = None,
        role: ServiceRole = "admin",
        *,
        exact_match: bool = False,
        title_id: int | None = None,
        has_links: bool | None = None,
        include_deleted: bool = False,
    ) -> list[NameSearchRow]:
        require_known_role(role, action="search_names")
        conditions: list[str] = []
        params: list[Any] = []

        normalized_query = normalize_with_raw(query).normalized_text
        if normalized_query is not None:
            if exact_match:
                conditions.append("n.normalized_name = ?")
                params.append(normalized_query)
            else:
                conditions.append("n.normalized_name LIKE ?")
                params.append(f"%{normalized_query}%")

        if title_id is not None:
            conditions.append(
                "EXISTS ("
                "SELECT 1 FROM name_subtitle_links l2 "
                "JOIN subtitles s2 ON s2.id = l2.subtitle_id "
                "WHERE l2.name_id = n.id AND l2.deleted_at IS NULL AND s2.title_id = ?"
                ")"
            )
            params.append(title_id)

        if has_links is not None:
            comparator = "> 0" if has_links else "= 0"
            conditions.append(
                "(SELECT COUNT(1) FROM name_subtitle_links l3 "
                "WHERE l3.name_id = n.id AND l3.deleted_at IS NULL) "
                f"{comparator}"
            )

        if not include_deleted:
            conditions.append("n.deleted_at IS NULL")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        rows = self._connection.execute(
            f"""
            SELECT
                n.id,
                n.raw_name,
                n.normalized_name,
                n.note,
                n.deleted_at,
                COUNT(DISTINCT l.id) AS linked_count,
                GROUP_CONCAT(DISTINCT s.title_id) AS title_ids
            FROM names n
            LEFT JOIN name_subtitle_links l
                ON l.name_id = n.id AND l.deleted_at IS NULL
            LEFT JOIN subtitles s
                ON s.id = l.subtitle_id
            {where_clause}
            GROUP BY n.id
            ORDER BY n.updated_at DESC, n.id DESC
            """,
            tuple(params),
        ).fetchall()

        return [
            NameSearchRow(
                id=int(row["id"]),
                raw_name=row["raw_name"],
                normalized_name=row["normalized_name"],
                note=row["note"],
                deleted_at=row["deleted_at"],
                linked_count=int(row["linked_count"]),
                title_ids=_parse_int_tuple(row["title_ids"]),
            )
            for row in rows
        ]

    def list_related_rows(
        self,
        name_id: int,
        role: ServiceRole = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[RelatedRow]:
        require_known_role(role, action="list_related_rows")
        rows = self._connection.execute(
            f"""
            SELECT
                l.id AS link_id,
                l.name_id,
                l.subtitle_id,
                s.title_id,
                l.relation_type,
                s.subtitle_code,
                s.subtitle_name,
                t.title_name,
                l.deleted_at AS link_deleted_at
            FROM name_subtitle_links l
            JOIN subtitles s ON s.id = l.subtitle_id
            JOIN titles t ON t.id = s.title_id
            WHERE l.name_id = ?
            {'AND l.deleted_at IS NULL' if not include_deleted else ''}
            ORDER BY t.title_name ASC, s.sort_order ASC, s.id ASC
            """,
            (name_id,),
        ).fetchall()

        return [
            RelatedRow(
                link_id=int(row["link_id"]),
                name_id=int(row["name_id"]),
                subtitle_id=int(row["subtitle_id"]),
                title_id=int(row["title_id"]),
                relation_type=row["relation_type"],
                subtitle_code=row["subtitle_code"],
                subtitle_name=row["subtitle_name"],
                title_name=row["title_name"],
                link_deleted_at=row["link_deleted_at"],
            )
            for row in rows
        ]

    def get_name_detail(self, name_id: int, role: ServiceRole = "admin") -> NameDetail:
        require_known_role(role, action="get_name_detail")
        row = self._fetch_one("names", name_id)
        return NameDetail(**row)

    def get_title_detail(self, title_id: int, role: ServiceRole = "admin") -> TitleDetail:
        require_known_role(role, action="get_title_detail")
        row = self._fetch_one("titles", title_id)
        return TitleDetail(**row)

    def get_subtitle_detail(self, subtitle_id: int, role: ServiceRole = "admin") -> SubtitleDetail:
        require_known_role(role, action="get_subtitle_detail")
        row = self._fetch_one("subtitles", subtitle_id)
        return SubtitleDetail(**row)

    def list_deleted_names(self, role: ServiceRole = "admin") -> list[NameDetail]:
        require_known_role(role, action="list_deleted_names")
        rows = self._list_deleted("names")
        return [NameDetail(**row) for row in rows]

    def list_titles(
        self, role: ServiceRole = "admin", *, include_deleted: bool = False
    ) -> list[TitleDetail]:
        require_known_role(role, action="list_titles")
        rows = self._connection.execute(
            """
            SELECT *
            FROM titles
            WHERE (? = 1 OR deleted_at IS NULL)
            ORDER BY updated_at DESC, id DESC
            """,
            (1 if include_deleted else 0,),
        ).fetchall()
        return [TitleDetail(**dict(row)) for row in rows]

    def list_names_for_title(
        self,
        title_id: int,
        role: ServiceRole = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[NameTitleLinkRow]:
        require_known_role(role, action="list_names_for_title")
        rows = self._connection.execute(
            f"""
            SELECT
                nt.id AS link_id,
                nt.name_id,
                nt.title_id,
                nt.relation_type,
                n.raw_name,
                t.title_name,
                nt.deleted_at AS link_deleted_at
            FROM name_title_links nt
            JOIN names n ON n.id = nt.name_id
            JOIN titles t ON t.id = nt.title_id
            WHERE nt.title_id = ?
            {"AND nt.deleted_at IS NULL" if not include_deleted else ""}
            ORDER BY n.raw_name ASC, nt.id ASC
            """,
            (title_id,),
        ).fetchall()
        return [
            NameTitleLinkRow(
                link_id=int(row["link_id"]),
                name_id=int(row["name_id"]),
                title_id=int(row["title_id"]),
                relation_type=row["relation_type"],
                raw_name=row["raw_name"],
                title_name=row["title_name"],
                link_deleted_at=row["link_deleted_at"],
            )
            for row in rows
        ]

    def list_subtitles(
        self,
        title_id: int,
        role: ServiceRole = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[SubtitleDetail]:
        require_known_role(role, action="list_subtitles")
        rows = self._connection.execute(
            """
            SELECT *
            FROM subtitles
            WHERE title_id = ? AND (? = 1 OR deleted_at IS NULL)
            ORDER BY sort_order ASC, id ASC
            """,
            (title_id, 1 if include_deleted else 0),
        ).fetchall()
        return [SubtitleDetail(**dict(row)) for row in rows]

    def list_deleted_titles(self, role: ServiceRole = "admin") -> list[TitleDetail]:
        require_known_role(role, action="list_deleted_titles")
        rows = self._list_deleted("titles")
        return [TitleDetail(**row) for row in rows]

    def list_deleted_subtitles(self, role: ServiceRole = "admin") -> list[SubtitleDetail]:
        require_known_role(role, action="list_deleted_subtitles")
        rows = self._list_deleted("subtitles")
        return [SubtitleDetail(**row) for row in rows]

    def list_deleted_links(self, role: ServiceRole = "admin") -> list[RelatedRow]:
        require_known_role(role, action="list_deleted_links")
        rows = self._connection.execute(
            """
            SELECT
                l.id AS link_id,
                l.name_id,
                l.subtitle_id,
                s.title_id,
                l.relation_type,
                s.subtitle_code,
                s.subtitle_name,
                t.title_name,
                l.deleted_at AS link_deleted_at
            FROM name_subtitle_links l
            JOIN subtitles s ON s.id = l.subtitle_id
            JOIN titles t ON t.id = s.title_id
            WHERE l.deleted_at IS NOT NULL
            ORDER BY l.deleted_at DESC, l.id DESC
            """
        ).fetchall()
        return [
            RelatedRow(
                link_id=int(row["link_id"]),
                name_id=int(row["name_id"]),
                subtitle_id=int(row["subtitle_id"]),
                title_id=int(row["title_id"]),
                relation_type=row["relation_type"],
                subtitle_code=row["subtitle_code"],
                subtitle_name=row["subtitle_name"],
                title_name=row["title_name"],
                link_deleted_at=row["link_deleted_at"],
            )
            for row in rows
        ]

    def list_change_logs(
        self,
        role: ServiceRole = "admin",
        *,
        entity_type: str | None = None,
        action: str | None = None,
        operator_id: str | None = None,
        created_from: str | None = None,
        created_to: str | None = None,
        limit: int = 200,
    ) -> list[ChangeLogRow]:
        require_known_role(role, action="list_change_logs")
        conditions: list[str] = []
        params: list[Any] = []

        if entity_type:
            conditions.append("entity_type = ?")
            params.append(entity_type)
        if action:
            conditions.append("action = ?")
            params.append(action)
        if operator_id:
            conditions.append("operator_id = ?")
            params.append(operator_id)
        if created_from:
            conditions.append("created_at >= ?")
            params.append(created_from)
        if created_to:
            conditions.append("created_at <= ?")
            params.append(created_to)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        rows = self._connection.execute(
            f"""
            SELECT
                id, entity_type, entity_id, action, operator_id, before_json, after_json, created_at
            FROM change_logs
            {where_clause}
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (*params, limit),
        ).fetchall()

        return [
            ChangeLogRow(
                id=int(row["id"]),
                entity_type=row["entity_type"],
                entity_id=int(row["entity_id"]),
                action=row["action"],
                operator_id=row["operator_id"],
                before_json=row["before_json"],
                after_json=row["after_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def _fetch_one(self, table: str, entity_id: int) -> dict[str, Any]:
        row = self._connection.execute(
            f"SELECT * FROM {table} WHERE id = ?", (entity_id,)
        ).fetchone()
        if row is None:
            raise NotFoundError(f"{table}({entity_id}) not found")
        return dict(row)

    def _list_deleted(self, table: str) -> list[dict[str, Any]]:
        rows = self._connection.execute(
            f"SELECT * FROM {table} WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC, id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def _parse_int_tuple(value: str | None) -> tuple[int, ...]:
    if not value:
        return ()
    return tuple(sorted({int(item) for item in value.split(",") if item}))

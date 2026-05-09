"""UI-oriented query service extensions.

This module keeps the existing QueryService API intact while extending the
name search behavior for the PySide6 application shell.
"""

from __future__ import annotations

from typing import Any

from app.application.authorization import ServiceRole, require_known_role
from app.application.query_services import QueryService, _parse_int_tuple
from app.application.read_models import NameSearchRow
from app.domain.normalization import normalize_with_raw


class EnhancedQueryService(QueryService):
    """QueryService variant used by the desktop UI.

    The main difference is that name search also searches related title and
    subtitle fields, and returns title/subtitle related counts separately.
    """

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
        display_query = (query or "").strip()
        if normalized_query is not None:
            if exact_match:
                conditions.append(
                    "(" 
                    "n.normalized_name = ? OR "
                    "EXISTS ("
                    "SELECT 1 FROM name_title_links ntq "
                    "JOIN titles tq ON tq.id = ntq.title_id "
                    "WHERE ntq.name_id = n.id AND ntq.deleted_at IS NULL "
                    "AND tq.deleted_at IS NULL AND tq.title_name = ?"
                    ") OR "
                    "EXISTS ("
                    "SELECT 1 FROM name_subtitle_links lq "
                    "JOIN subtitles sq ON sq.id = lq.subtitle_id "
                    "JOIN titles ttq ON ttq.id = sq.title_id "
                    "WHERE lq.name_id = n.id AND lq.deleted_at IS NULL "
                    "AND sq.deleted_at IS NULL "
                    "AND (sq.subtitle_name = ? OR sq.subtitle_code = ? OR ttq.title_name = ?)"
                    ")"
                    ")"
                )
                params.extend([normalized_query, display_query, display_query, display_query, display_query])
            else:
                like_normalized = f"%{normalized_query}%"
                like_display = f"%{display_query}%"
                conditions.append(
                    "(" 
                    "n.normalized_name LIKE ? OR "
                    "EXISTS ("
                    "SELECT 1 FROM name_title_links ntq "
                    "JOIN titles tq ON tq.id = ntq.title_id "
                    "WHERE ntq.name_id = n.id AND ntq.deleted_at IS NULL "
                    "AND tq.deleted_at IS NULL AND tq.title_name LIKE ?"
                    ") OR "
                    "EXISTS ("
                    "SELECT 1 FROM name_subtitle_links lq "
                    "JOIN subtitles sq ON sq.id = lq.subtitle_id "
                    "JOIN titles ttq ON ttq.id = sq.title_id "
                    "WHERE lq.name_id = n.id AND lq.deleted_at IS NULL "
                    "AND sq.deleted_at IS NULL "
                    "AND (sq.subtitle_name LIKE ? OR sq.subtitle_code LIKE ? OR ttq.title_name LIKE ?)"
                    ")"
                    ")"
                )
                params.extend([like_normalized, like_display, like_display, like_display, like_display])

        if title_id is not None:
            conditions.append(
                "("
                "EXISTS ("
                "SELECT 1 FROM name_subtitle_links l2 "
                "JOIN subtitles s2 ON s2.id = l2.subtitle_id "
                "WHERE l2.name_id = n.id AND l2.deleted_at IS NULL AND s2.title_id = ?"
                ") OR EXISTS ("
                "SELECT 1 FROM name_title_links nt2 "
                "WHERE nt2.name_id = n.id AND nt2.deleted_at IS NULL AND nt2.title_id = ?"
                ")"
                ")"
            )
            params.extend([title_id, title_id])

        if has_links is not None:
            comparator = "> 0" if has_links else "= 0"
            conditions.append(
                "((SELECT COUNT(1) FROM name_subtitle_links l3 "
                "WHERE l3.name_id = n.id AND l3.deleted_at IS NULL) + "
                "(SELECT COUNT(1) FROM name_title_links nt3 "
                "WHERE nt3.name_id = n.id AND nt3.deleted_at IS NULL)) "
                f"{comparator}"
            )

        if not include_deleted:
            conditions.append("n.deleted_at IS NULL")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        rows = self._connection.execute(
            f"""
            SELECT
                n.id,
                n.public_id,
                n.raw_name,
                n.normalized_name,
                n.note,
                n.deleted_at,
                (SELECT COUNT(DISTINCT ntc.id) FROM name_title_links ntc
                 WHERE ntc.name_id = n.id AND ntc.deleted_at IS NULL) AS title_related_count,
                (SELECT COUNT(DISTINCT lsc.id) FROM name_subtitle_links lsc
                 WHERE lsc.name_id = n.id AND lsc.deleted_at IS NULL) AS subtitle_related_count,
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

        result: list[NameSearchRow] = []
        for row in rows:
            title_count = int(row["title_related_count"])
            subtitle_count = int(row["subtitle_related_count"])
            result.append(
                NameSearchRow(
                    id=int(row["id"]),
                    raw_name=row["raw_name"],
                    normalized_name=row["normalized_name"],
                    note=row["note"],
                    deleted_at=row["deleted_at"],
                    linked_count=title_count + subtitle_count,
                    title_ids=_parse_int_tuple(row["title_ids"]),
                    public_id=row["public_id"],
                    title_related_count=title_count,
                    subtitle_related_count=subtitle_count,
                )
            )
        return result

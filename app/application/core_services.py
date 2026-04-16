"""Core services for names/titles/subtitles/links."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.domain.errors import ConflictError, NotFoundError, StateTransitionError, ValidationError
from app.domain.normalization import normalize_for_comparison


@dataclass(frozen=True)
class NameInput:
    raw_name: str
    note: str | None = None
    icon_path: str | None = None


@dataclass(frozen=True)
class TitleInput:
    title_name: str
    note: str | None = None
    icon_path: str | None = None


@dataclass(frozen=True)
class SubtitleInput:
    title_id: int
    subtitle_code: str
    subtitle_name: str
    sort_order: int = 0
    note: str | None = None
    icon_path: str | None = None


class CoreService:
    """Application service for core entity operations."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute("PRAGMA foreign_keys = ON;")

    def create_name(self, payload: NameInput, operator_id: str) -> int:
        self._validate_operator_id(operator_id)
        normalized_name = normalize_for_comparison(payload.raw_name)
        now = _utc_now()
        try:
            cursor = self._connection.execute(
                """
                INSERT INTO names(
                    raw_name, normalized_name, note, icon_path, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.raw_name,
                    normalized_name,
                    payload.note,
                    payload.icon_path,
                    now,
                    now,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ConflictError("name already exists") from exc

        name_id = _require_lastrowid(cursor)
        self._insert_change_log(
            "names", name_id, "create", operator_id, None, self._get_name(name_id)
        )
        return name_id

    def update_name(self, name_id: int, payload: NameInput, operator_id: str) -> None:
        self._validate_operator_id(operator_id)
        before = self._get_name(name_id)
        if before["deleted_at"] is not None:
            raise StateTransitionError("cannot update deleted name")

        normalized_name = normalize_for_comparison(payload.raw_name)
        now = _utc_now()
        try:
            self._connection.execute(
                """
                UPDATE names
                SET raw_name = ?, normalized_name = ?, note = ?, icon_path = ?, updated_at = ?
                WHERE id = ?
                """,
                (payload.raw_name, normalized_name, payload.note, payload.icon_path, now, name_id),
            )
        except sqlite3.IntegrityError as exc:
            raise ConflictError("name already exists") from exc

        self._insert_change_log(
            "names", name_id, "update", operator_id, before, self._get_name(name_id)
        )

    def delete_name(self, name_id: int, operator_id: str) -> None:
        self._logical_delete("names", name_id, operator_id)

    def restore_name(self, name_id: int, operator_id: str) -> None:
        self._restore("names", name_id, operator_id)

    def hard_delete_name(self, name_id: int, operator_id: str) -> None:
        self._hard_delete("names", name_id, operator_id)

    def create_title(self, payload: TitleInput, operator_id: str) -> int:
        self._validate_operator_id(operator_id)
        now = _utc_now()
        cursor = self._connection.execute(
            """
            INSERT INTO titles(title_name, note, icon_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (payload.title_name, payload.note, payload.icon_path, now, now),
        )
        title_id = _require_lastrowid(cursor)
        self._insert_change_log(
            "titles", title_id, "create", operator_id, None, self._get_title(title_id)
        )
        return title_id

    def update_title(self, title_id: int, payload: TitleInput, operator_id: str) -> None:
        self._validate_operator_id(operator_id)
        before = self._get_title(title_id)
        if before["deleted_at"] is not None:
            raise StateTransitionError("cannot update deleted title")

        now = _utc_now()
        self._connection.execute(
            """
            UPDATE titles
            SET title_name = ?, note = ?, icon_path = ?, updated_at = ?
            WHERE id = ?
            """,
            (payload.title_name, payload.note, payload.icon_path, now, title_id),
        )
        self._insert_change_log(
            "titles", title_id, "update", operator_id, before, self._get_title(title_id)
        )

    def delete_title(self, title_id: int, operator_id: str) -> None:
        self._logical_delete("titles", title_id, operator_id)

    def restore_title(self, title_id: int, operator_id: str) -> None:
        self._restore("titles", title_id, operator_id)

    def hard_delete_title(self, title_id: int, operator_id: str) -> None:
        self._hard_delete("titles", title_id, operator_id)

    def create_subtitle(self, payload: SubtitleInput, operator_id: str) -> int:
        self._validate_operator_id(operator_id)
        self._assert_active("titles", payload.title_id)

        now = _utc_now()
        try:
            cursor = self._connection.execute(
                """
                INSERT INTO subtitles(
                    title_id, subtitle_code, subtitle_name, sort_order, note, icon_path,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.title_id,
                    payload.subtitle_code,
                    payload.subtitle_name,
                    payload.sort_order,
                    payload.note,
                    payload.icon_path,
                    now,
                    now,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ConflictError("subtitle already exists for title") from exc

        subtitle_id = _require_lastrowid(cursor)
        self._insert_change_log(
            "subtitles", subtitle_id, "create", operator_id, None, self._get_subtitle(subtitle_id)
        )
        return subtitle_id

    def update_subtitle(self, subtitle_id: int, payload: SubtitleInput, operator_id: str) -> None:
        self._validate_operator_id(operator_id)
        before = self._get_subtitle(subtitle_id)
        if before["deleted_at"] is not None:
            raise StateTransitionError("cannot update deleted subtitle")

        self._assert_active("titles", payload.title_id)
        now = _utc_now()
        try:
            self._connection.execute(
                """
                UPDATE subtitles
                SET title_id = ?, subtitle_code = ?, subtitle_name = ?, sort_order = ?,
                    note = ?, icon_path = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    payload.title_id,
                    payload.subtitle_code,
                    payload.subtitle_name,
                    payload.sort_order,
                    payload.note,
                    payload.icon_path,
                    now,
                    subtitle_id,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ConflictError("subtitle already exists for title") from exc

        self._insert_change_log(
            "subtitles", subtitle_id, "update", operator_id, before, self._get_subtitle(subtitle_id)
        )

    def delete_subtitle(self, subtitle_id: int, operator_id: str) -> None:
        self._logical_delete("subtitles", subtitle_id, operator_id)

    def restore_subtitle(self, subtitle_id: int, operator_id: str) -> None:
        self._restore("subtitles", subtitle_id, operator_id)

    def hard_delete_subtitle(self, subtitle_id: int, operator_id: str) -> None:
        self._hard_delete("subtitles", subtitle_id, operator_id)

    def link_name_to_subtitle(
        self, name_id: int, subtitle_id: int, relation_type: str, operator_id: str
    ) -> int:
        self._validate_operator_id(operator_id)
        if not relation_type.strip():
            raise ValidationError("relation_type must not be blank")

        self._assert_active("names", name_id)
        self._assert_active("subtitles", subtitle_id)

        existing = self._connection.execute(
            """
            SELECT id, deleted_at FROM name_subtitle_links
            WHERE name_id = ? AND subtitle_id = ?
            """,
            (name_id, subtitle_id),
        ).fetchone()

        now = _utc_now()
        if existing is None:
            cursor = self._connection.execute(
                """
                INSERT INTO name_subtitle_links(
                    name_id, subtitle_id, relation_type, deleted_at, created_at, updated_at
                ) VALUES (?, ?, ?, NULL, ?, ?)
                """,
                (name_id, subtitle_id, relation_type, now, now),
            )
            link_id = _require_lastrowid(cursor)
            self._insert_change_log(
                "name_subtitle_links",
                link_id,
                "link",
                operator_id,
                None,
                self._get_link(link_id),
            )
            return link_id

        link_id = int(existing["id"])
        before = self._get_link(link_id)
        self._connection.execute(
            """
            UPDATE name_subtitle_links
            SET relation_type = ?, deleted_at = NULL, updated_at = ?
            WHERE id = ?
            """,
            (relation_type, now, link_id),
        )
        self._insert_change_log(
            "name_subtitle_links", link_id, "link", operator_id, before, self._get_link(link_id)
        )
        return link_id

    def unlink_name_from_subtitle(self, link_id: int, operator_id: str) -> None:
        self._validate_operator_id(operator_id)
        before = self._get_link(link_id)
        if before["deleted_at"] is not None:
            raise StateTransitionError("link already deleted")

        now = _utc_now()
        self._connection.execute(
            "UPDATE name_subtitle_links SET deleted_at = ?, updated_at = ? WHERE id = ?",
            (now, now, link_id),
        )
        self._insert_change_log(
            "name_subtitle_links", link_id, "unlink", operator_id, before, self._get_link(link_id)
        )

    def _logical_delete(self, table: str, entity_id: int, operator_id: str) -> None:
        self._validate_operator_id(operator_id)
        before = self._get_entity(table, entity_id)
        if before["deleted_at"] is not None:
            raise StateTransitionError(f"{table} already deleted")

        now = _utc_now()
        self._connection.execute(
            f"UPDATE {table} SET deleted_at = ?, updated_at = ? WHERE id = ?",
            (now, now, entity_id),
        )
        self._insert_change_log(
            table,
            entity_id,
            "delete",
            operator_id,
            before,
            self._get_entity(table, entity_id),
        )

    def _restore(self, table: str, entity_id: int, operator_id: str) -> None:
        self._validate_operator_id(operator_id)
        before = self._get_entity(table, entity_id)
        if before["deleted_at"] is None:
            raise StateTransitionError(f"{table} is active")

        now = _utc_now()
        try:
            self._connection.execute(
                f"UPDATE {table} SET deleted_at = NULL, updated_at = ? WHERE id = ?",
                (now, entity_id),
            )
        except sqlite3.IntegrityError as exc:
            raise ConflictError(f"{table} conflicts on restore") from exc

        self._insert_change_log(
            table,
            entity_id,
            "restore",
            operator_id,
            before,
            self._get_entity(table, entity_id),
        )

    def _hard_delete(self, table: str, entity_id: int, operator_id: str) -> None:
        self._validate_operator_id(operator_id)
        before = self._get_entity(table, entity_id)
        if before["deleted_at"] is None:
            raise StateTransitionError(f"{table} must be logically deleted first")

        self._connection.execute(f"DELETE FROM {table} WHERE id = ?", (entity_id,))
        self._insert_change_log(table, entity_id, "hard_delete", operator_id, before, None)

    def _assert_active(self, table: str, entity_id: int) -> None:
        entity = self._get_entity(table, entity_id)
        if entity["deleted_at"] is not None:
            raise StateTransitionError(f"{table} is deleted")

    def _get_name(self, name_id: int) -> dict[str, Any]:
        return self._get_entity("names", name_id)

    def _get_title(self, title_id: int) -> dict[str, Any]:
        return self._get_entity("titles", title_id)

    def _get_subtitle(self, subtitle_id: int) -> dict[str, Any]:
        return self._get_entity("subtitles", subtitle_id)

    def _get_link(self, link_id: int) -> dict[str, Any]:
        return self._get_entity("name_subtitle_links", link_id)

    def _get_entity(self, table: str, entity_id: int) -> dict[str, Any]:
        row = self._connection.execute(
            f"SELECT * FROM {table} WHERE id = ?", (entity_id,)
        ).fetchone()
        if row is None:
            raise NotFoundError(f"{table}({entity_id}) not found")
        return dict(row)

    def _insert_change_log(
        self,
        entity_type: str,
        entity_id: int,
        action: str,
        operator_id: str,
        before: dict[str, Any] | None,
        after: dict[str, Any] | None,
    ) -> None:
        self._connection.execute(
            """
            INSERT INTO change_logs(
                entity_type, entity_id, action, operator_id, before_json, after_json, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entity_type,
                entity_id,
                action,
                operator_id,
                _to_json(before),
                _to_json(after),
                _utc_now(),
            ),
        )

    @staticmethod
    def _validate_operator_id(operator_id: str) -> None:
        if not operator_id.strip():
            raise ValidationError("operator_id must not be blank")


def _to_json(value: dict[str, Any] | None) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _require_lastrowid(cursor: sqlite3.Cursor) -> int:
    if cursor.lastrowid is None:
        raise RuntimeError("lastrowid is not available")
    return int(cursor.lastrowid)

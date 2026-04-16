"""Read models used by query services."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NameSearchRow:
    id: int
    raw_name: str
    normalized_name: str
    note: str | None
    deleted_at: str | None
    linked_count: int
    title_ids: tuple[int, ...]


@dataclass(frozen=True)
class NameDetail:
    id: int
    raw_name: str
    normalized_name: str
    note: str | None
    icon_path: str | None
    deleted_at: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class TitleDetail:
    id: int
    title_name: str
    note: str | None
    icon_path: str | None
    deleted_at: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class SubtitleDetail:
    id: int
    title_id: int
    subtitle_code: str
    subtitle_name: str
    sort_order: int
    note: str | None
    icon_path: str | None
    deleted_at: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class RelatedRow:
    link_id: int
    name_id: int
    subtitle_id: int
    title_id: int
    relation_type: str
    subtitle_code: str
    subtitle_name: str
    title_name: str
    link_deleted_at: str | None


@dataclass(frozen=True)
class ChangeLogRow:
    id: int
    entity_type: str
    entity_id: int
    action: str
    operator_id: str
    before_json: str | None
    after_json: str | None
    created_at: str

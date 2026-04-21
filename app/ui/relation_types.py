"""Relation type candidates for Link management UI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RelationTypeOption:
    value: str
    label: str


RELATION_TYPE_OPTIONS: tuple[RelationTypeOption, ...] = (
    RelationTypeOption(value="primary", label="primary（主関連）"),
    RelationTypeOption(value="secondary", label="secondary（副関連）"),
    RelationTypeOption(value="alias", label="alias（別名）"),
    RelationTypeOption(value="other", label="その他（手入力）"),
)

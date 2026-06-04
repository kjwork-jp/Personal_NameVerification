"""Tests for duplicate entity candidate detection."""

from __future__ import annotations

import sqlite3

from scripts.detect_duplicate_entities import (
    EntityRecord,
    fetch_entity_records,
    find_duplicate_groups,
)


def test_find_duplicate_groups_detects_display_exact_match() -> None:
    records = [
        EntityRecord(entity_kind="names", entity_id=1, display_value="Alice Sample"),
        EntityRecord(entity_kind="names", entity_id=2, display_value="Alice Sample"),
        EntityRecord(entity_kind="names", entity_id=3, display_value="alice sample"),
    ]

    groups = find_duplicate_groups(records, key_types=("display",))

    assert len(groups) == 1
    assert groups[0].entity_kind == "names"
    assert groups[0].key_type == "display"
    assert groups[0].key_value == "Alice Sample"
    assert [record.entity_id for record in groups[0].records] == [1, 2]


def test_find_duplicate_groups_detects_normalized_candidates() -> None:
    records = [
        EntityRecord(
            entity_kind="titles",
            entity_id=1,
            display_value="Demo Title",
            normalized_value="demo title",
        ),
        EntityRecord(
            entity_kind="titles",
            entity_id=2,
            display_value="Ｄｅｍｏ　Ｔｉｔｌｅ",
            normalized_value="demo title",
        ),
        EntityRecord(
            entity_kind="titles",
            entity_id=3,
            display_value="Another Title",
            normalized_value="another title",
        ),
        EntityRecord(
            entity_kind="titles",
            entity_id=4,
            display_value="",
            normalized_value=None,
        ),
        EntityRecord(
            entity_kind="titles",
            entity_id=5,
            display_value=" ",
            normalized_value=None,
        ),
    ]

    groups = find_duplicate_groups(records, key_types=("normalized",))

    assert len(groups) == 1
    assert groups[0].entity_kind == "titles"
    assert groups[0].key_type == "normalized"
    assert groups[0].key_value == "demo title"
    assert [record.entity_id for record in groups[0].records] == [1, 2]


def test_fetch_entity_records_excludes_deleted_rows_by_default() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE names (
            id INTEGER PRIMARY KEY,
            raw_name TEXT NOT NULL,
            normalized_name TEXT NOT NULL,
            deleted_at TEXT
        );
        CREATE TABLE titles (
            id INTEGER PRIMARY KEY,
            title_name TEXT NOT NULL,
            deleted_at TEXT
        );
        CREATE TABLE subtitles (
            id INTEGER PRIMARY KEY,
            title_id INTEGER NOT NULL,
            subtitle_code TEXT NOT NULL,
            subtitle_name TEXT NOT NULL,
            deleted_at TEXT
        );
        INSERT INTO names(id, raw_name, normalized_name, deleted_at)
        VALUES
            (1, 'Alice', 'alice', NULL),
            (2, 'Alice', 'alice', '2026-01-01T00:00:00Z');
        INSERT INTO titles(id, title_name, deleted_at)
        VALUES
            (1, 'Main Title', NULL),
            (2, 'MAIN TITLE', NULL);
        INSERT INTO subtitles(id, title_id, subtitle_code, subtitle_name, deleted_at)
        VALUES
            (1, 1, 'S-001', 'Chapter 1', NULL),
            (2, 1, 'S-002', 'Chapter 1', '2026-01-01T00:00:00Z');
        """
    )

    active_records = fetch_entity_records(connection, include_deleted=False)
    all_records = fetch_entity_records(connection, include_deleted=True)

    assert {(record.entity_kind, record.entity_id) for record in active_records} == {
        ("names", 1),
        ("titles", 1),
        ("titles", 2),
        ("subtitles", 1),
    }
    assert {(record.entity_kind, record.entity_id) for record in all_records} == {
        ("names", 1),
        ("names", 2),
        ("titles", 1),
        ("titles", 2),
        ("subtitles", 1),
        ("subtitles", 2),
    }

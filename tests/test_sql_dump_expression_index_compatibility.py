"""SQL dump compatibility tests for app-only expression indexes."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from app.infrastructure.db import initialize_database
from app.infrastructure.export_backup import export_sql_dump


def test_sql_dump_omits_app_only_expression_indexes_for_portable_restore(tmp_path: Path) -> None:
    source = initialize_database(tmp_path / "source.db")
    try:
        source.execute("INSERT INTO titles(title_name) VALUES (?)", ("Demo",))
        dump_path = export_sql_dump(source, tmp_path / "dump.sql")
    finally:
        source.close()

    dump_text = dump_path.read_text("utf-8")
    assert "app_normalize(" not in dump_text
    assert "uq_titles_active_display_name" not in dump_text
    assert "uq_subtitles_active_title_display_name" not in dump_text

    restored = sqlite3.connect(tmp_path / "restored.db")
    try:
        restored.executescript(dump_text)
        row = restored.execute("SELECT title_name FROM titles").fetchone()
        assert row == ("Demo",)
    finally:
        restored.close()


def test_sql_dump_preserves_rows_containing_index_like_text(tmp_path: Path) -> None:
    source = initialize_database(tmp_path / "source-with-text.db")
    index_like_text = "create index uq_titles_active_display_name app_normalize("
    try:
        source.execute(
            "INSERT INTO titles(title_name, note) VALUES (?, ?)",
            ("Demo", index_like_text),
        )
        dump_path = export_sql_dump(source, tmp_path / "dump-with-text.sql")
    finally:
        source.close()

    restored = sqlite3.connect(tmp_path / "restored-with-text.db")
    try:
        restored.executescript(dump_path.read_text("utf-8"))
        row = restored.execute("SELECT note FROM titles").fetchone()
        assert row == (index_like_text,)
    finally:
        restored.close()

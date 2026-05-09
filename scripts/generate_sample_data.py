"""Generate sample CSV files or a SQLite DB for validation.

Examples:
    python scripts/generate_sample_data.py --format sqlite --output tmp/sample.db --names 1000000
    python scripts/generate_sample_data.py --format csv --output tmp/sample_csv --names 1000000
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path

from app.infrastructure.db import initialize_database

DEFAULT_NAMES = 1000
DEFAULT_TITLES = 1000
DEFAULT_SUBTITLES_PER_TITLE = 3
DEFAULT_LINKS_PER_NAME = 2
BATCH_SIZE = 5000


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate sample data for NameVerification.")
    parser.add_argument("--format", choices=["sqlite", "csv"], default="sqlite")
    parser.add_argument("--output", required=True, help="Output DB path or CSV directory")
    parser.add_argument("--names", type=int, default=DEFAULT_NAMES)
    parser.add_argument("--titles", type=int, default=DEFAULT_TITLES)
    parser.add_argument("--subtitles-per-title", type=int, default=DEFAULT_SUBTITLES_PER_TITLE)
    parser.add_argument("--links-per-name", type=int, default=DEFAULT_LINKS_PER_NAME)
    args = parser.parse_args()

    output = Path(args.output)
    if args.format == "sqlite":
        generate_sqlite(
            db_path=output,
            name_count=args.names,
            title_count=args.titles,
            subtitles_per_title=args.subtitles_per_title,
            links_per_name=args.links_per_name,
        )
    else:
        generate_csv(
            output_dir=output,
            name_count=args.names,
            title_count=args.titles,
            subtitles_per_title=args.subtitles_per_title,
            links_per_name=args.links_per_name,
        )
    return 0


def generate_sqlite(
    *,
    db_path: Path,
    name_count: int,
    title_count: int,
    subtitles_per_title: int,
    links_per_name: int,
) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    connection = initialize_database(db_path)
    connection.execute("PRAGMA synchronous = OFF")
    connection.execute("PRAGMA journal_mode = WAL")
    now = "2026-01-01T00:00:00Z"

    _bulk_insert(
        connection,
        """
        INSERT INTO names(raw_name, normalized_name, note, icon_path, deleted_at, created_at, updated_at)
        VALUES (?, ?, ?, NULL, NULL, ?, ?)
        """,
        (
            (f"sample-name-{i:07d}", f"sample-name-{i:07d}", f"sample note {i}", now, now)
            for i in range(1, name_count + 1)
        ),
    )
    _bulk_insert(
        connection,
        """
        INSERT INTO titles(title_name, note, icon_path, deleted_at, created_at, updated_at)
        VALUES (?, ?, NULL, NULL, ?, ?)
        """,
        ((f"sample-title-{i:07d}", f"title note {i}", now, now) for i in range(1, title_count + 1)),
    )

    subtitle_total = title_count * subtitles_per_title
    _bulk_insert(
        connection,
        """
        INSERT INTO subtitles(title_id, subtitle_code, subtitle_name, sort_order, note, icon_path, deleted_at, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, NULL, NULL, ?, ?)
        """,
        (
            (
                ((i - 1) // subtitles_per_title) + 1,
                f"SUB-{i:07d}",
                f"sample-subtitle-{i:07d}",
                (i - 1) % subtitles_per_title,
                f"subtitle note {i}",
                now,
                now,
            )
            for i in range(1, subtitle_total + 1)
        ),
    )

    link_total = min(name_count * links_per_name, max(name_count, subtitle_total))
    _bulk_insert(
        connection,
        """
        INSERT OR IGNORE INTO name_title_links(name_id, title_id, relation_type, deleted_at, created_at, updated_at)
        VALUES (?, ?, 'primary', NULL, ?, ?)
        """,
        (
            (name_id, ((name_id - 1) % title_count) + 1, now, now)
            for name_id in range(1, name_count + 1)
        ),
    )
    _bulk_insert(
        connection,
        """
        INSERT OR IGNORE INTO name_subtitle_links(name_id, subtitle_id, relation_type, deleted_at, created_at, updated_at)
        VALUES (?, ?, 'primary', NULL, ?, ?)
        """,
        (
            (((i - 1) % name_count) + 1, ((i - 1) % subtitle_total) + 1, now, now)
            for i in range(1, link_total + 1)
        ),
    )
    connection.commit()
    connection.close()
    print(f"Generated SQLite sample DB: {db_path}")


def generate_csv(
    *,
    output_dir: Path,
    name_count: int,
    title_count: int,
    subtitles_per_title: int,
    links_per_name: int,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    now = "2026-01-01T00:00:00Z"
    _write_csv(
        output_dir / "names.csv",
        ["raw_name", "normalized_name", "note", "created_at", "updated_at"],
        ((f"sample-name-{i:07d}", f"sample-name-{i:07d}", f"sample note {i}", now, now) for i in range(1, name_count + 1)),
    )
    _write_csv(
        output_dir / "titles.csv",
        ["title_name", "note", "created_at", "updated_at"],
        ((f"sample-title-{i:07d}", f"title note {i}", now, now) for i in range(1, title_count + 1)),
    )
    subtitle_total = title_count * subtitles_per_title
    _write_csv(
        output_dir / "subtitles.csv",
        ["title_id", "subtitle_code", "subtitle_name", "sort_order", "note", "created_at", "updated_at"],
        (
            (
                ((i - 1) // subtitles_per_title) + 1,
                f"SUB-{i:07d}",
                f"sample-subtitle-{i:07d}",
                (i - 1) % subtitles_per_title,
                f"subtitle note {i}",
                now,
                now,
            )
            for i in range(1, subtitle_total + 1)
        ),
    )
    link_total = min(name_count * links_per_name, max(name_count, subtitle_total))
    _write_csv(
        output_dir / "name_subtitle_links.csv",
        ["name_id", "subtitle_id", "relation_type", "created_at", "updated_at"],
        (
            (((i - 1) % name_count) + 1, ((i - 1) % subtitle_total) + 1, "primary", now, now)
            for i in range(1, link_total + 1)
        ),
    )
    print(f"Generated CSV sample directory: {output_dir}")


def _bulk_insert(connection: sqlite3.Connection, sql: str, rows: object) -> None:
    batch: list[tuple[object, ...]] = []
    for row in rows:
        batch.append(tuple(row))
        if len(batch) >= BATCH_SIZE:
            connection.executemany(sql, batch)
            batch.clear()
    if batch:
        connection.executemany(sql, batch)


def _write_csv(path: Path, headers: list[str], rows: object) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        batch_count = 0
        for row in rows:
            writer.writerow(row)
            batch_count += 1
            if batch_count % 100000 == 0:
                handle.flush()


if __name__ == "__main__":
    raise SystemExit(main())

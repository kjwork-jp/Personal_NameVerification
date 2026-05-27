"""Generate sample CSV files or a SQLite DB for validation.

Examples:
    python scripts/generate_sample_data.py --format sqlite --output tmp/sample.db --names 1000000
    python scripts/generate_sample_data.py --format csv --output tmp/sample_csv --names 1000000
    python scripts/generate_sample_data.py --preset demo --format sqlite --output tmp/demo.db
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path

from app.application.password_services import hash_password
from app.infrastructure.db import initialize_database

DEFAULT_NAMES = 1000
DEFAULT_TITLES = 1000
DEFAULT_SUBTITLES_PER_TITLE = 3
DEFAULT_LINKS_PER_NAME = 2
BATCH_SIZE = 5000
DEMO_TIMESTAMP = "2026-01-01T00:00:00Z"
UAT_DELETED_TIMESTAMP = "2026-01-02T00:00:00Z"
DEMO_PASSWORDS: dict[str, str] = {
    "demo-viewer": "demo-viewer-pass",
    "demo-editor": "demo-editor-pass",
    "demo-admin": "demo-admin-pass",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate sample data for NameVerification.")
    parser.add_argument("--preset", choices=["bulk", "demo"], default="bulk")
    parser.add_argument("--format", choices=["sqlite", "csv"], default="sqlite")
    parser.add_argument("--output", required=True, help="Output DB path or CSV directory")
    parser.add_argument("--names", type=int, default=DEFAULT_NAMES)
    parser.add_argument("--titles", type=int, default=DEFAULT_TITLES)
    parser.add_argument("--subtitles-per-title", type=int, default=DEFAULT_SUBTITLES_PER_TITLE)
    parser.add_argument("--links-per-name", type=int, default=DEFAULT_LINKS_PER_NAME)
    args = parser.parse_args()

    output = Path(args.output)
    if args.preset == "demo":
        if args.format == "sqlite":
            generate_demo_sqlite(db_path=output)
        else:
            generate_demo_csv(output_dir=output)
        return 0

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


def generate_demo_sqlite(*, db_path: Path) -> None:
    """Generate a small, meaningful SQLite DB for demo/UAT use."""

    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    connection = initialize_database(db_path)
    try:
        _insert_demo_business_data(connection)
        _insert_demo_users(connection)
        connection.commit()
    finally:
        connection.close()
    print(f"Generated demo SQLite sample DB: {db_path}")
    print("Demo users: demo-viewer / demo-editor / demo-admin")
    print("Demo passwords are documented constants for local demo use only.")


def generate_demo_csv(*, output_dir: Path) -> None:
    """Generate small CSV files for import/export demonstrations."""

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_dir / "names.csv",
        ["raw_name", "normalized_name", "note", "created_at", "updated_at"],
        (
            (raw_name, normalized_name, note, DEMO_TIMESTAMP, DEMO_TIMESTAMP)
            for raw_name, normalized_name, note in _demo_names()
        ),
    )
    _write_csv(
        output_dir / "titles.csv",
        ["title_name", "note", "created_at", "updated_at"],
        (
            (title_name, note, DEMO_TIMESTAMP, DEMO_TIMESTAMP)
            for title_name, note in _demo_titles()
        ),
    )
    _write_csv(
        output_dir / "subtitles.csv",
        [
            "title_id",
            "subtitle_code",
            "subtitle_name",
            "sort_order",
            "note",
            "created_at",
            "updated_at",
        ],
        (
            (title_id, code, name, sort_order, note, DEMO_TIMESTAMP, DEMO_TIMESTAMP)
            for title_id, code, name, sort_order, note in _demo_subtitles()
        ),
    )
    _write_csv(
        output_dir / "name_title_links.csv",
        ["name_id", "title_id", "relation_type", "created_at", "updated_at"],
        (
            (name_id, title_id, "primary", DEMO_TIMESTAMP, DEMO_TIMESTAMP)
            for name_id, title_id in _demo_name_title_links()
        ),
    )
    _write_csv(
        output_dir / "name_subtitle_links.csv",
        ["name_id", "subtitle_id", "relation_type", "created_at", "updated_at"],
        (
            (name_id, subtitle_id, "primary", DEMO_TIMESTAMP, DEMO_TIMESTAMP)
            for name_id, subtitle_id in _demo_name_subtitle_links()
        ),
    )
    print(f"Generated demo CSV sample directory: {output_dir}")


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
    now = DEMO_TIMESTAMP

    _bulk_insert(
        connection,
        """
        INSERT INTO names(raw_name, normalized_name, note, icon_path, deleted_at, created_at, updated_at)
        VALUES (?, ?, ?, NULL, NULL, ?, ?)
        """,
        (
            (
                f"sample-name-{i:07d}",
                f"sample-name-{i:07d}",
                f"sample note {i}",
                now,
                now,
            )
            for i in range(1, name_count + 1)
        ),
    )
    _bulk_insert(
        connection,
        """
        INSERT INTO titles(title_name, note, icon_path, deleted_at, created_at, updated_at)
        VALUES (?, ?, NULL, NULL, ?, ?)
        """,
        (
            (f"sample-title-{i:07d}", f"title note {i}", now, now)
            for i in range(1, title_count + 1)
        ),
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
        VALUES (?, ?, ?, NULL, ?, ?)
        """,
        _bulk_name_subtitle_link_rows(
            name_count=name_count,
            subtitle_total=subtitle_total,
            links_per_name=links_per_name,
            now=now,
        ),
    )
    _seed_bulk_deleted_and_change_log_rows(
        connection,
        name_count=name_count,
        title_count=title_count,
        subtitle_total=subtitle_total,
        now=now,
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
    now = DEMO_TIMESTAMP
    _write_csv(
        output_dir / "names.csv",
        ["raw_name", "normalized_name", "note", "created_at", "updated_at"],
        (
            (
                f"sample-name-{i:07d}",
                f"sample-name-{i:07d}",
                f"sample note {i}",
                now,
                now,
            )
            for i in range(1, name_count + 1)
        ),
    )
    _write_csv(
        output_dir / "titles.csv",
        ["title_name", "note", "created_at", "updated_at"],
        (
            (f"sample-title-{i:07d}", f"title note {i}", now, now)
            for i in range(1, title_count + 1)
        ),
    )
    subtitle_total = title_count * subtitles_per_title
    _write_csv(
        output_dir / "subtitles.csv",
        [
            "title_id",
            "subtitle_code",
            "subtitle_name",
            "sort_order",
            "note",
            "created_at",
            "updated_at",
        ],
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
    _write_csv(
        output_dir / "name_subtitle_links.csv",
        ["name_id", "subtitle_id", "relation_type", "created_at", "updated_at"],
        _bulk_name_subtitle_link_rows(
            name_count=name_count,
            subtitle_total=subtitle_total,
            links_per_name=links_per_name,
            now=now,
        ),
    )
    print(f"Generated CSV sample directory: {output_dir}")


def _bulk_name_subtitle_link_rows(
    *,
    name_count: int,
    subtitle_total: int,
    links_per_name: int,
    now: str,
) -> object:
    """Yield deterministic unique name-subtitle links for bulk/UAT data.

    The row count is capped only by the number of unique (name_id, subtitle_id)
    combinations so `links_per_name` is reflected in medium-sized UAT data.
    """

    if name_count <= 0 or subtitle_total <= 0 or links_per_name <= 0:
        return
    for name_id in range(1, name_count + 1):
        for offset in range(links_per_name):
            subtitle_id = ((name_id + offset - 1) % subtitle_total) + 1
            yield (name_id, subtitle_id, "primary", now, now)


def _seed_bulk_deleted_and_change_log_rows(
    connection: sqlite3.Connection,
    *,
    name_count: int,
    title_count: int,
    subtitle_total: int,
    now: str,
) -> None:
    """Seed soft-deleted rows and change logs for manual UAT review."""

    deleted_at = UAT_DELETED_TIMESTAMP
    if name_count >= 1:
        connection.execute(
            """
            UPDATE names
            SET deleted_at = ?, updated_at = ?, note = note || ' / UAT deleted name'
            WHERE id = ?
            """,
            (deleted_at, now, name_count),
        )
    if name_count >= 2:
        connection.execute(
            """
            UPDATE names
            SET deleted_at = ?, updated_at = ?, note = note || ' / UAT hard-delete candidate'
            WHERE id = ?
            """,
            (deleted_at, now, name_count - 1),
        )
    if title_count >= 1:
        connection.execute(
            """
            UPDATE titles
            SET deleted_at = ?, updated_at = ?, note = note || ' / UAT deleted title'
            WHERE id = ?
            """,
            (deleted_at, now, title_count),
        )
    if subtitle_total >= 1:
        connection.execute(
            """
            UPDATE subtitles
            SET deleted_at = ?, updated_at = ?, note = note || ' / UAT deleted subtitle'
            WHERE id = ?
            """,
            (deleted_at, now, subtitle_total),
        )

    connection.execute(
        """
        UPDATE name_title_links
        SET deleted_at = ?, updated_at = ?
        WHERE id = (SELECT MAX(id) FROM name_title_links)
        """,
        (deleted_at, now),
    )
    connection.execute(
        """
        UPDATE name_subtitle_links
        SET deleted_at = ?, updated_at = ?
        WHERE id IN (
            SELECT id FROM name_subtitle_links ORDER BY id DESC LIMIT 3
        )
        """,
        (deleted_at, now),
    )
    connection.executemany(
        """
        INSERT INTO change_logs(
            entity_type, entity_id, action, operator_id, before_json, after_json, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "names",
                max(name_count, 1),
                "soft_delete",
                "uat-admin",
                '{"deleted_at": null}',
                f'{{"deleted_at": "{deleted_at}"}}',
                now,
            ),
            (
                "titles",
                max(title_count, 1),
                "soft_delete",
                "uat-admin",
                '{"deleted_at": null}',
                f'{{"deleted_at": "{deleted_at}"}}',
                now,
            ),
            (
                "subtitles",
                max(subtitle_total, 1),
                "soft_delete",
                "uat-admin",
                '{"deleted_at": null}',
                f'{{"deleted_at": "{deleted_at}"}}',
                now,
            ),
            (
                "name_subtitle_links",
                1,
                "review_seed",
                "uat-editor",
                None,
                '{"note": "UAT change log seed"}',
                now,
            ),
        ],
    )


def _insert_demo_business_data(connection: sqlite3.Connection) -> None:
    now = DEMO_TIMESTAMP
    _bulk_insert(
        connection,
        """
        INSERT INTO names(raw_name, normalized_name, note, icon_path, deleted_at, created_at, updated_at)
        VALUES (?, ?, ?, NULL, NULL, ?, ?)
        """,
        (
            (raw_name, normalized_name, note, now, now)
            for raw_name, normalized_name, note in _demo_names()
        ),
    )
    _bulk_insert(
        connection,
        """
        INSERT INTO titles(title_name, note, icon_path, deleted_at, created_at, updated_at)
        VALUES (?, ?, NULL, NULL, ?, ?)
        """,
        ((title_name, note, now, now) for title_name, note in _demo_titles()),
    )
    _bulk_insert(
        connection,
        """
        INSERT INTO subtitles(title_id, subtitle_code, subtitle_name, sort_order, note, icon_path, deleted_at, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, NULL, NULL, ?, ?)
        """,
        (
            (title_id, code, name, sort_order, note, now, now)
            for title_id, code, name, sort_order, note in _demo_subtitles()
        ),
    )
    _bulk_insert(
        connection,
        """
        INSERT INTO name_title_links(name_id, title_id, relation_type, deleted_at, created_at, updated_at)
        VALUES (?, ?, 'primary', NULL, ?, ?)
        """,
        ((name_id, title_id, now, now) for name_id, title_id in _demo_name_title_links()),
    )
    _bulk_insert(
        connection,
        """
        INSERT INTO name_subtitle_links(name_id, subtitle_id, relation_type, deleted_at, created_at, updated_at)
        VALUES (?, ?, 'primary', NULL, ?, ?)
        """,
        ((name_id, subtitle_id, now, now) for name_id, subtitle_id in _demo_name_subtitle_links()),
    )


def _insert_demo_users(connection: sqlite3.Connection) -> None:
    now = DEMO_TIMESTAMP
    users = [
        ("demo-viewer", "Demo Viewer", "viewer"),
        ("demo-editor", "Demo Editor", "editor"),
        ("demo-admin", "Demo Admin", "admin"),
    ]
    rows = []
    for index, (operator_id, display_name, role) in enumerate(users, start=1):
        password = DEMO_PASSWORDS[operator_id]
        salt = f"demo-salt-{index:06d}".encode()
        hashed = hash_password(password, salt_bytes=salt)
        rows.append(
            (
                operator_id,
                display_name,
                role,
                hashed.password_hash,
                hashed.salt,
                hashed.algorithm,
                hashed.iterations,
                now,
                now,
                now,
            )
        )
    connection.executemany(
        """
        INSERT INTO users(
            operator_id, display_name, role, password_hash, password_salt,
            password_algorithm, password_iterations, password_updated_at, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )


def _demo_names() -> list[tuple[str, str, str]]:
    return [
        ("Alice Sample", "alice sample", "viewer/editor/adminで検索確認しやすい名前"),
        ("Bob Demo", "bob demo", "タイトル複数関連の確認用"),
        ("Carol UAT", "carol uat", "サブタイトル関連の確認用"),
        ("Deleted Candidate", "deleted candidate", "削除操作確認用の候補"),
        ("Export Check", "export check", "export/import確認用"),
    ]


def _demo_titles() -> list[tuple[str, str]]:
    return [
        ("Demo Title Alpha", "基本検索と関連数確認用"),
        ("Demo Title Beta", "複数名前関連の確認用"),
        ("Operations Title", "export/backup確認用"),
    ]


def _demo_subtitles() -> list[tuple[int, str, str, int, str]]:
    return [
        (1, "ALPHA-001", "Alpha Episode 1", 1, "初期表示確認"),
        (1, "ALPHA-002", "Alpha Episode 2", 2, "関連確認"),
        (2, "BETA-001", "Beta Episode 1", 1, "検索確認"),
        (3, "OPS-001", "Operations Export", 1, "出力確認"),
    ]


def _demo_name_title_links() -> list[tuple[int, int]]:
    return [(1, 1), (2, 1), (2, 2), (3, 2), (5, 3)]


def _demo_name_subtitle_links() -> list[tuple[int, int]]:
    return [(1, 1), (2, 2), (3, 3), (5, 4)]


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
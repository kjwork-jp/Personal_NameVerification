# NameVerification v3

NameVerification v3 is a **PySide6 desktop application** for local/offline name verification and management.

This repository is **not docs-only**: it already contains implementation code, SQLite schema, and automated tests.

## Current implementation status

Implemented layers:
- `app/domain`: normalization rules and domain errors
- `app/application`: `CoreService` / `QueryService` / read models / minimal authorization helpers
- `app/infrastructure`: SQLite schema application helpers
- `app/ui`: PySide6 UI tabs and role-based UI guards
- `db/`: schema and migration SQL
- `tests/`: unit + UI tests

## Runtime / stack

- Python 3.12+
- PySide6 (desktop UI)
- SQLite (local DB)

## Entry point

- `app/pyside6_main.py`

## Main window tabs

- Search
- Name Management
- Title / Subtitle Management
- Link Management
- Trash
- Audit Log
- Operations

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e .
```

## Run application

```bash
python -m app.pyside6_main
```

## Test / checks

```bash
pytest -q
ruff check .
black --check .
mypy app
```

## Export / backup create foundation (service layer)

The application/infrastructure layers now provide file output helpers for:
- CSV export (`names`, `titles`, `subtitles`, `name_subtitle_links`, `change_logs`)
- JSON export (same table set)
- SQL dump export (SQLite `iterdump`)
- backup file create (SQLite file copy)
- backup restore foundation (backup file -> target DB file replacement)
- CSV / JSON import foundation (empty SQLite DB only, admin only)

Import scope note: SQL import is out of scope; DB-wide replacement is handled by restore foundation.

Restore RBAC: restore is destructive and allowed for `admin` only (`viewer` / `editor` are rejected).

Restore safety note: close active SQLite connections for the target DB before running restore.

Current RBAC: export/backup create operations are allowed for `editor` / `admin`, and rejected for `viewer`.

Operations tab provides minimal UI entrypoints for export/import/backup/restore using path inputs, Browse buttons, and execution buttons.
- Browse buttons use native file/directory dialog for path selection.
- Recent path history is persisted per input (max 5, deduplicated, latest-first) and offered via completer.
- Operation execution results are appended to local JSONL (`operations_events.jsonl`) under AppDataLocation with `timestamp/action/role/status/message/path` fields (best-effort write).
- Operation execution uses async worker foundation (QThreadPool/QRunnable), with busy-state guard, duplicate-start prevention, and minimum cancel-request UI.
- Local housekeeping controls: log size-based rotation + TTL pruning for archived JSONL logs, and a single-click recent path history clear button.

## Notes

- The app uses a local SQLite database and is intended for single-site local operation.
- README/docs wording may be refined over time; functional behavior should be validated against code + tests.

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

## Notes

- The app uses a local SQLite database and is intended for single-site local operation.
- README/docs wording may be refined over time; functional behavior should be validated against code + tests.

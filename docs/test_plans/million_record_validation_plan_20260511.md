# Million Record Validation Plan (2026-05-11)

## Purpose

Validate NameVerification v3 after the PySide6 UI redesign with large generated datasets. The focus is search, list refresh, tab reload, Windows EXE startup, SQLite persistence, DB change logs, and automatic JSONL change log export.

## Rules

- Do not commit million-record generated data to the repository.
- Use generated sample data, not personal data.
- Use a dedicated validation database path.
- SQLite `change_logs` is the source of truth. JSONL export is an operational aid.

## Data scale

| Stage | names | titles | subtitles | links | Goal |
|---:|---:|---:|---:|---:|---|
| 1 | 10,000 | 1,000 | 5,000 | 10,000 | light smoke |
| 2 | 100,000 | 10,000 | 50,000 | 100,000 | practical scale |
| 3 | 1,000,000 | 100,000 | 500,000 | 1,000,000 | upper-scale validation |

## Validation points

| No | Area | Pass criteria |
|---:|---|---|
| 1 | database generation | validation DB is created without error |
| 2 | app startup | Python entrypoint and EXE both start |
| 3 | Search tab | cross-entity search works for names, titles, and subtitles |
| 4 | Name tab | list, filter, update, and move-to-trash work |
| 5 | Title and Subtitle tabs | dropdown selection, list rendering, create, and update work |
| 6 | Relation tab | unrelated and related dropdowns remain usable |
| 7 | Trash tab | entity classification, restore, and hard delete work |
| 8 | Audit log tab | before, after, and diff rendering work |
| 9 | Operations tab | export, backup, and operations log display work |
| 10 | JSONL export | change operations append JSONL records |

## Measurements

| Metric | Record |
|---|---|
| startup time | elapsed time until main window appears |
| search latency | response time per representative query |
| tab reload latency | Search, Name, Title, Subtitle, Trash, Audit |
| memory usage | after startup, after search, after repeated operations |
| database size | SQLite size per stage |
| JSONL size | size and rotation behavior after write operations |
| UI layout | horizontal scroll, column widths, blank space, clipping |

## Commands

Set validation-only paths before running the app.

```powershell
$env:NAMEVERIFICATION_DB_PATH = "C:/tmp/nameverification_million.db"
$env:NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH = "C:/tmp/nameverification_change_logs.jsonl"
python .\scripts\generate_sample_data.py --help
python -m app.pyside6_main
.\scripts\build_exe_windows.ps1
.\scripts\smoke_test_exe_windows.ps1
```

Increase the data scale in stage order after confirming the generation script options.

## Stop conditions

- The application cannot start.
- Search or tab reload freezes the UI for an unacceptable duration.
- SQLite persistence, restore, or backup behavior breaks.
- JSONL export failure affects the database transaction.

## Output

Record results in the handoff workbook and, if needed, add detailed result files under `docs/test_results/`.

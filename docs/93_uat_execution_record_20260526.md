# 93_uat_execution_record_20260526.md

## Purpose

This document records the actual execution result for `V900-UAT-001`.

Do not paste sensitive data, passwords, generated DB contents, or screenshots that expose private data.

## Baseline

| Item | Value |
|---|---|
| UAT plan | `docs/91_uat_execution_plan_20260526.md` |
| UAT checklist | `docs/92_uat_checklist_20260526.md` |
| Execution record | this file |
| Release gate | Deferred until UAT complete |

## Execution summary

| Item | Value |
|---|---|
| Execution date | 2026-05-26 |
| Executor | NAOKI KAJIWARA |
| OS | Windows / PowerShell |
| Python / EXE mode | Python module execution |
| DB path | `tmp/uat_demo.db` |
| CSV source path | `tmp/uat_demo_csv` |
| Overall status | IN PROGRESS |

## Setup result

| ID | Result | Notes |
|---|---|---|
| SETUP-001 | PASS | Demo SQLite DB generated at `tmp/uat_demo.db`. |
| SETUP-002 | PASS | Demo CSV source generated at `tmp/uat_demo_csv`. |
| SETUP-003 | PASS | `git status --short tmp` returned no tracked/untracked tmp entries. |
| SETUP-004 | NOT RUN | Initial template command `python -m app.main` was invalid. Corrected command is `python -m app.pyside6_main`. |
| SETUP-005 | NOT RUN | Confirm Help / Settings shows DB/log/export/backup paths after successful startup. |

## Scenario result summary

| Group | Result | Notes |
|---|---|---|
| UAT-01 Startup / Login | NOT RUN |  |
| UAT-02 Viewer role | NOT RUN |  |
| UAT-03 Editor role | NOT RUN |  |
| UAT-04 Admin role | NOT RUN |  |
| UAT-05 Data operations | NOT RUN |  |
| UAT-06 Audit / Security | NOT RUN |  |
| UAT-07 Documentation match | NOT RUN |  |

## Detailed findings

| Finding ID | Severity | Related check | Summary | Decision | Follow-up |
|---|---|---|---|---|---|
| UAT-F-001 | documentation fix | SETUP-004 | UAT execution record used invalid launch command `python -m app.main`. | Fixed in record. Continue with corrected command. | Use `python -m app.pyside6_main`. |

## Blocker status

| Item | Status | Notes |
|---|---|---|
| Any blocker found | NO | Current issue was command documentation, not application blocker. |
| Any fix-before-release found | NOT RUN |  |
| Any documentation fix found | YES | Launch command corrected in this record. |
| Any accepted limitation recorded | NOT RUN |  |

## Exit decision

| Item | Status | Notes |
|---|---|---|
| All required checks executed | NOT RUN |  |
| No unresolved blocker remains | IN PROGRESS | No blocker currently identified. |
| UAT complete | NOT RUN |  |
| Release preparation allowed | NOT RUN | Only after UAT complete |

## Local execution commands

Generate demo SQLite DB:

```powershell
python .\scripts\generate_sample_data.py --preset demo --format sqlite --output tmp\uat_demo.db
```

Generate demo CSV source:

```powershell
python .\scripts\generate_sample_data.py --preset demo --format csv --output tmp\uat_demo_csv
```

Confirm generated files are not tracked:

```powershell
git status --short tmp
```

Run application against UAT DB for local testing:

```powershell
$env:NAMEVERIFICATION_DB_PATH = "tmp\uat_demo.db"
python -m app.pyside6_main
```

Clear UAT DB path after testing:

```powershell
Remove-Item Env:\NAMEVERIFICATION_DB_PATH -ErrorAction SilentlyContinue
```

## Notes

- Keep generated UAT data under `tmp/`.
- Do not commit generated DB/CSV/export/backup/log outputs.
- Record only non-sensitive summary evidence in this file.
- Release preparation remains deferred until UAT is complete.

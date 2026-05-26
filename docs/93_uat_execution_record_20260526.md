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
| SETUP-004 | PASS | Application started with corrected command `python -m app.pyside6_main` and intended DB path. |
| SETUP-005 | PASS | Help / Settings showed DB path `tmp\\uat_demo.db`, DB exists, JSONL log path, operations log path, and backup default path. |

## Scenario result summary

| Group | Result | Notes |
|---|---|---|
| UAT-01 Startup / Login | PASS | viewer/editor/admin role login and role-specific banner/status were observed. Operator IDs observed in UI were `viewer`, `editor`, and `admin`. |
| UAT-02 Viewer role | IN PROGRESS | Viewer role screen and banner were observed. Specific restriction checks remain. |
| UAT-03 Editor role | IN PROGRESS | Editor role screen and banner were observed. Create/update/export checks remain. |
| UAT-04 Admin role | IN PROGRESS | Admin role screen, banner, and user management list were observed. Admin operation checks remain. |
| UAT-05 Data operations | NOT RUN |  |
| UAT-06 Audit / Security | IN PROGRESS | Help / Settings operation memo, protection warning, path diagnostics, and password logging guidance observed. |
| UAT-07 Documentation match | IN PROGRESS | Launch command documentation fix recorded. Help / Settings guidance visually matches current UI. Demo operator ID wording discrepancy was recorded. |

## Detailed findings

| Finding ID | Severity | Related check | Summary | Decision | Follow-up |
|---|---|---|---|---|---|
| UAT-F-001 | documentation fix | SETUP-004 | UAT execution record used invalid launch command `python -m app.main`. | Fixed in record. Continue with corrected command. | Use `python -m app.pyside6_main`. |
| UAT-F-002 | documentation fix | UAT-01 | UAT guidance expected `demo-viewer` / `demo-editor` / `demo-admin`, while screenshots showed active operator IDs `viewer` / `editor` / `admin`. | Role validation accepted; clarify demo DB/user wording before final UAT closure. | Reconcile checklist/manual wording with actual generated or selected UAT DB users. |

## Completed checks from screenshots/logs

| ID | Result | Notes |
|---|---|---|
| UAT-01-001 | PASS | Viewer login observed. Window/status showed `viewer` role and viewer role banner. |
| UAT-01-002 | PASS | Editor login observed. Window/status showed `editor` role and editor role banner. |
| UAT-01-003 | PASS | Admin login observed. Window/status showed `admin` role, admin role banner, and user management tab. |
| UAT-01-004 | PASS | Role banner displayed role-specific text and allowed/restricted summary for viewer/editor/admin. |
| UAT-04-002 | IN PROGRESS | Admin user management list was visible with three users. Create/role change/disable/enable operations were not yet executed. |
| UAT-06-004 | PASS | Help / Settings file protection checklist/guidance area was visible. |
| UAT-06-005 | PASS | Path diagnostics and protection warning showed ACL guidance including `Get-Acl` / `icacls` wording. |
| UAT-06-006 | PASS | Password logging guidance stated password/password_hash/password_salt are not recorded. |
| UAT-07-004 | PASS | Help / Settings guidance matched current implementation areas for paths, logs, backup, and protection notes. |

## Blocker status

| Item | Status | Notes |
|---|---|---|
| Any blocker found | NO | Current findings are documentation/wording issues, not application blockers. |
| Any fix-before-release found | NOT RUN |  |
| Any documentation fix found | YES | Launch command corrected; demo operator ID wording still needs reconciliation before final closure. |
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

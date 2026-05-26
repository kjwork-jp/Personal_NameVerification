# 92_uat_checklist_20260526.md

## Purpose

Executable UAT checklist for `V900-UAT-001`.

Use this checklist to record manual UAT status. Do not commit generated DB/CSV/export/backup files.

## Status legend

| Status | Meaning |
|---|---|
| NOT RUN | Not executed yet |
| PASS | Expected behavior confirmed |
| FAIL | Unexpected behavior found |
| N/A | Not applicable with reason |
| ACCEPTED | Known limitation accepted |

## UAT setup checklist

| ID | Status | Check | Evidence / Notes |
|---|---|---|---|
| SETUP-001 | NOT RUN | Generate demo SQLite DB under `tmp/uat_demo.db`. |  |
| SETUP-002 | NOT RUN | Generate demo CSV source under `tmp/uat_demo_csv`. |  |
| SETUP-003 | NOT RUN | Confirm generated files are not tracked by git. |  |
| SETUP-004 | NOT RUN | Confirm application starts with the intended DB path. |  |
| SETUP-005 | NOT RUN | Confirm Help / Settings shows DB/log/export/backup paths. |  |

## UAT-01 Startup / Login

| ID | Status | Check | Evidence / Notes |
|---|---|---|---|
| UAT-01-001 | NOT RUN | Login as `demo-viewer`. |  |
| UAT-01-002 | NOT RUN | Login as `demo-editor`. |  |
| UAT-01-003 | NOT RUN | Login as `demo-admin`. |  |
| UAT-01-004 | NOT RUN | Role banner text and allowed/restricted summary are role-specific. |  |
| UAT-01-005 | NOT RUN | Failed login does not log password or password-like values. |  |

## UAT-02 Viewer role

| ID | Status | Check | Evidence / Notes |
|---|---|---|---|
| UAT-02-001 | NOT RUN | Viewer can search and inspect related details. |  |
| UAT-02-002 | NOT RUN | Viewer cannot create or update names/titles/subtitles. |  |
| UAT-02-003 | NOT RUN | Viewer cannot perform export/backup/import/restore. |  |
| UAT-02-004 | NOT RUN | Viewer cannot access destructive operations. |  |
| UAT-02-005 | NOT RUN | Viewer sees clear restriction messages/tooltips. |  |

## UAT-03 Editor role

| ID | Status | Check | Evidence / Notes |
|---|---|---|---|
| UAT-03-001 | NOT RUN | Editor can create and update normal records. |  |
| UAT-03-002 | NOT RUN | Editor can create backup. |  |
| UAT-03-003 | NOT RUN | Editor can run allowed exports including sanitized JSON. |  |
| UAT-03-004 | NOT RUN | Sanitized JSON excludes auth/admin/settings/audit/change-log tables. |  |
| UAT-03-005 | NOT RUN | Editor cannot restore/import/delete/fully delete/user-manage. |  |

## UAT-04 Admin role

| ID | Status | Check | Evidence / Notes |
|---|---|---|---|
| UAT-04-001 | NOT RUN | Admin can perform delete/restore/complete delete with confirmation. |  |
| UAT-04-002 | NOT RUN | Admin can manage users and roles. |  |
| UAT-04-003 | NOT RUN | Admin can review user audit logs. |  |
| UAT-04-004 | NOT RUN | Admin can run import preview and import on an empty target DB. |  |
| UAT-04-005 | NOT RUN | Admin-only destructive actions are clearly separated from normal workflow. |  |

## UAT-05 Data operations

| ID | Status | Check | Evidence / Notes |
|---|---|---|---|
| UAT-05-001 | NOT RUN | CSV export creates expected files. |  |
| UAT-05-002 | NOT RUN | JSON export creates full application data export. |  |
| UAT-05-003 | NOT RUN | SQL dump is treated as protected full DB dump. |  |
| UAT-05-004 | NOT RUN | Backup creates a DB copy under the expected folder. |  |
| UAT-05-005 | NOT RUN | CSV import preview reports counts, missing tables, invalid tables, and unknown files. |  |
| UAT-05-006 | NOT RUN | JSON import preview reports counts, missing tables, invalid tables, and unknown keys. |  |
| UAT-05-007 | NOT RUN | Import rejects non-empty target DB. |  |

## UAT-06 Audit / Security

| ID | Status | Check | Evidence / Notes |
|---|---|---|---|
| UAT-06-001 | NOT RUN | Operation history shows before/after/diff. |  |
| UAT-06-002 | NOT RUN | Visible audit log review JSON export works. |  |
| UAT-06-003 | NOT RUN | Operations log records export/backup/import/restore actions. |  |
| UAT-06-004 | NOT RUN | Help / Settings file protection checklist is visible. |  |
| UAT-06-005 | NOT RUN | Help / Settings ACL guidance includes `Get-Acl` and `icacls`. |  |
| UAT-06-006 | NOT RUN | Password/password_hash/password_salt are not visible in audit displays. |  |

## UAT-07 Documentation match

| ID | Status | Check | Evidence / Notes |
|---|---|---|---|
| UAT-07-001 | NOT RUN | Quick start manual matches current tabs. |  |
| UAT-07-002 | NOT RUN | Feature guide matches current RBAC. |  |
| UAT-07-003 | NOT RUN | Detailed operation procedure matches current data operations. |  |
| UAT-07-004 | NOT RUN | Help / Settings guidance matches current implementation. |  |

## Findings register

| Finding ID | Severity | Related check | Summary | Decision | Follow-up |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## UAT exit decision

| Item | Status | Notes |
|---|---|---|
| All checks complete | NOT RUN |  |
| No blocker remains | NOT RUN |  |
| Release preparation allowed | NOT RUN | Only after UAT is complete |

## Commands

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

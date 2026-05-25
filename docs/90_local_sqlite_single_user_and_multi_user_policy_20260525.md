# 90_local_sqlite_single_user_and_multi_user_policy_20260525.md

## Purpose

This document defines the current architecture policy for local SQLite usage and the decision criteria for future multi-user expansion.

This is a design and operations ledger. It does not change application behavior by itself.

## Current position

NameVerification is currently a local desktop application using a local SQLite database file.

The in-app authentication and RBAC model controls UI/application operations, but it does not make the SQLite file a server-side multi-user database.

## Current supported model

| Area | Policy |
|---|---|
| Runtime | Local desktop application |
| Database | Local SQLite file |
| Primary usage | Single operator at a time per database file |
| RBAC | In-app control for application operations |
| File protection | OS ACL / BitLocker / EFS / folder permissions are required for file-level protection |
| Network share | Not recommended as a multi-user database strategy |
| Concurrent writes | Not treated as a supported operational scenario |

## Explicit constraints

- Multiple people opening and writing the same SQLite DB file at the same time is not a supported target.
- Shared folders do not replace a server-side DB, lock management, or application-level transaction design.
- App-level RBAC does not prevent direct OS-level access to DB/backup/export/log files.
- Backup, restore, import, and SQL dump operations are destructive or sensitive and require operator discipline.

## Safe operating patterns

| Pattern | Status | Notes |
|---|---|---|
| One user / one local DB | Supported | Default and safest model |
| One operator edits, others receive export | Supported | Use sanitized JSON/CSV where appropriate |
| Periodic backup then manual handoff | Supported with care | Confirm backup/export scope and file protection |
| Shared DB on network drive | Not recommended | Risk of locking, corruption, and unclear ownership |
| Multi-user concurrent editing | Not supported | Requires server architecture or conflict strategy |

## Future multi-user options

| Option | Summary | Trade-off |
|---|---|---|
| SQLite + strict operator schedule | Keep local DB, enforce one editor at a time | Low implementation cost, high operational discipline |
| SQLite + sync/handoff workflow | Explicit export/import or backup handoff | Safer than shared writes, still manual |
| Local service API | App talks to a local/server API instead of direct DB file | More implementation work, clearer control point |
| PostgreSQL/Supabase backend | Move to server-side DB with auth and concurrency controls | Stronger multi-user model, higher ops/design cost |
| Web app rewrite | Convert UI/API/backend into web architecture | Highest flexibility, largest scope |

## Decision criteria for moving beyond local SQLite

Consider server-side or API-backed architecture when any of the following becomes true:

1. Multiple operators need concurrent edits.
2. DB file must be centrally managed with reliable access control.
3. Audit logs need tamper-resistant storage.
4. External users need access without receiving local DB/export files.
5. Backup/restore/import ownership must be centralized.
6. Conflict resolution becomes a recurring operational issue.
7. Data volume or UI responsiveness requires query pagination/server-side filtering.

## Recommended future path

| Phase | Direction |
|---|---|
| Current | Keep local SQLite single-operator model |
| Near-term | Improve export/import/backup/audit workflows and file protection guidance |
| Before multi-user | Define data ownership, locking, conflict, audit, backup, and auth requirements |
| Multi-user candidate | Introduce service/API layer or server-side database |

## Non-goals

- Do not implement multi-user support in this task.
- Do not introduce a server database in this task.
- Do not change current local login behavior in this task.
- Do not treat shared network folders as an approved multi-user architecture.
- Do not start UAT or release preparation.

## Operational guidance

Until a future architecture change is explicitly implemented:

1. Treat one SQLite DB file as owned by one active operator at a time.
2. Use backup/export for handoff rather than concurrent shared editing.
3. Protect DB/backup/export/log files at the OS level.
4. Do not put the DB on an uncontrolled shared folder.
5. Document any handoff process using operations log and change log timestamps.

# v0.2.0-rc1 Release Evidence

Date: 2026-05-20
Updated: 2026-05-21

## Summary

- Release package creation: PASS
- EXE rebuild: PASS
- EXE freshness check during packaging: PASS
- Portable smoke: PASS after retry
- Portable GUI basic check: PASS
- Quality gates: PASS
- P1 authentication negative-path UAT: PASS
- P1 last active admin protection UAT: PASS for role demotion and disable protection. User delete operation was not applicable in the current UI.
- P1 Data I/O file-output UAT: PASS for admin and editor export/backup/operations-log evidence.
- P1 audit-log UAT: PASS for login failure, role change, disable, and enable evidence.
- P1 restore current-DB handling: PASS by `RESTORE-LOCK-001`. GUI restore to the currently opened DB is now blocked before destructive confirmation and before the restore service is called.
- P1 import UAT: PARTIAL PASS. JSON import from exported JSON completed with before-import backup; invalid import coverage remains to be confirmed if required.

## Package

- Folder: `release/v0.2.0-rc1`
- Zip: `release/NameVerification-v0.2.0-rc1-portable.zip`
- Manifest: `release/v0.2.0-rc1/00_manifest_v0.2.0-rc1_20260520.csv`
- Checksums: `release/v0.2.0-rc1/70_release_evidence/checksums_sha256_v0.2.0-rc1_20260520.txt`

## Build and package verification

- `scripts/build_exe_windows.ps1`: PASS
- `scripts/package_release_windows.ps1 -ReleaseName v0.2.0-rc1`: PASS
- EXE freshness check: PASS
- `scripts/smoke_test_portable_windows.ps1`: first run exited with code 0 during smoke check, second run PASS

## Runtime paths confirmed

- `30_prod_db/nameverification.db`
- `40_logs/change_logs.jsonl`
- `40_logs/operations_events.jsonl`
- `50_backups/daily`
- `60_exports/csv`
- `60_exports/json`
- `60_exports/sql`

## Portable GUI checks

- No extra child windows remained.
- Main window only was shown.
- Account switching did not leave a white window.
- Account switching did not leave extra child windows.
- Account switching did not leave a stale process.
- Windows authentication logged in as viewer.
- Help / Settings showed package root under `release/v0.2.0-rc1`.
- Help / Settings showed DB path under `30_prod_db`.
- Help / Settings showed logs under `40_logs`.
- Data I/O paths pointed to the portable folder layout.
- Export defaults pointed to `60_exports/csv`, `60_exports/json`, and `60_exports/sql`.
- Backup defaults pointed to `30_prod_db/nameverification.db` and `50_backups/daily`.
- Restore defaults pointed to `50_backups/daily` and `30_prod_db/nameverification.db`.
- Import defaults pointed to `60_exports/csv` and `60_exports/json`.

## P1 UAT evidence

### AUTH-002

- Initial admin setup: PASS.
- Correct admin login: PASS.
- Incorrect admin password: PASS. The login was rejected and `login_failure` was recorded with `reason=credential_mismatch`.
- Unknown local operator: PASS. The login was rejected and `login_failure` was recorded with `reason=not_found`.
- Empty operator id: PASS by GUI evidence. The login dialog requested an operator id.
- Disabled user login: PASS. The login was rejected and `login_failure` was recorded with `reason=disabled`.
- Password material in user audit logs: PASS. `user_audit_logs` before/after JSON does not include `password`, `password_hash`, `password_salt`, or `password_iterations` values.

### ADMIN-001

- Last active admin demotion protection: PASS. GUI displayed `cannot demote the last active admin`.
- Last active admin disable protection: PASS. GUI displayed `cannot disable the last active admin`.
- Last active admin delete protection: not applicable in the current user-management UI because user delete is not exposed as a tested operation.

### DATAIO-002

- Admin CSV export: PASS. CSV files were created under `60_exports/csv`.
- Admin JSON export: PASS. JSON export was created under `60_exports/json`.
- Admin SQL dump export: PASS. SQL dump was created under `60_exports/sql`.
- Admin backup: PASS. Backup DB was created under `50_backups/daily`.
- Editor backup: PASS. Backup DB was created under `50_backups/daily` with role `editor`.
- Editor CSV/JSON/SQL export: PASS. Export logs show success with role `editor`.
- Operations Log persistence: PASS. `40_logs/operations_events.jsonl` existed and included export/backup/import/restore entries.
- Note: SQL dump is a full DB dump and contains the `users` table schema/data including password hash/salt fields. This is expected for a full DB dump but the generated SQL file must be treated as protected material.

### RESTORE-001 / Import

- Restore to current DB from GUI: previously FAIL/BLOCKED with WinError 5 while replacing `30_prod_db/nameverification.db` from `.restore_tmp`.
- `RESTORE-LOCK-001`: PASS. Current-DB restore is now blocked in the GUI before `confirm_destructive_action` and before `backup_restore_service.restore_database` is called.
- Restore before-backup path: evidence exists under `50_backups/before_restore` from the earlier failing restore attempt.
- JSON import from exported JSON: PASS. Import completed with zero data rows and created a before-import backup under `50_backups/before_import`.
- Invalid restore/import input: not fully evidenced in the provided log set.

### RESTORE-LOCK-001 validation

- `pytest -q`: PASS.
- `ruff check .`: PASS.
- `black --check .`: PASS.
- `mypy app`: PASS.
- Regression tests added for block / allow / no-op / idempotent behavior.

### AUDIT-002

- login_failure audit: PASS.
- user_disable audit: PASS.
- user_enable audit: PASS by screenshot evidence.
- user_role_change audit: PASS by screenshot evidence.
- password non-recording in audit log: PASS for user audit JSON fields. Full SQL dump remains protected material as noted above.

## Current blockers / follow-up checks

- Confirm invalid restore/import inputs do not create before-operation backups unless already covered by automated tests.
- Decide whether SQL dump should remain a full DB dump or whether a sanitized application-data-only export mode is needed for sharing.

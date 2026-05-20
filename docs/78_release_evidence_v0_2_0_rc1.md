# v0.2.0-rc1 Release Evidence

Date: 2026-05-20

## Summary

- Release package creation: PASS
- EXE rebuild: PASS
- EXE freshness check during packaging: PASS
- Portable smoke: PASS after retry
- Portable GUI basic check: PASS
- Quality gates: PASS

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

## Remaining checks

- Authentication negative-path UAT
- Last active admin protection UAT
- Data I/O file-output UAT
- Restore and import UAT on a disposable copy
- Audit-log negative-path UAT

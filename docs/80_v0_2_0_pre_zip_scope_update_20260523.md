# 80_v0_2_0_pre_zip_scope_update_20260523.md

## Purpose

Record the scope update made after v0.2.0-rc1 tag/package/smoke and the final v0.2.0 promotion.

## Decision

v0.2.0-rc1 was tagged, built, packaged, and smoke-tested successfully, but it is treated as a checkpoint rather than the final distribution candidate.

The final zip creation flow was deferred until the remaining future-improvement items were completed inside the v0.2.0 scope. Those implementation P1 items completed, v0.2.0-rc2 packaging/smoke completed successfully, the rc2 GitHub Release was published as a pre-release, external ledgers were synchronized, and v0.2.0 has now been promoted to a stable GitHub Release.

## Current stable release

- Stable release: v0.2.0
- Tag: pushed
- GitHub Release: published / stable release
- Build: PASS
- Package: PASS
- Portable smoke: PASS
- Final zip: `release/NameVerification-v0.2.0-portable.zip`
- Manifest: `release/v0.2.0/00_manifest_v0.2.0_20260525.csv`
- Checksums: `release/v0.2.0/70_release_evidence/checksums_sha256_v0.2.0_20260525.txt`
- Final stable evidence: docs/83_release_final_v0_2_0_20260525.md

## Previous checkpoints

- v0.2.0-rc1: checkpoint only
- v0.2.0-rc2: release candidate / GitHub pre-release published
- Remote branches: `main` only after cleanup
- rc2 final evidence: docs/81_release_final_v0_2_0_rc2_20260525.md
- rc2 external ledger evidence: docs/82_external_ledger_sync_v0_2_0_rc2_20260525.md

## v0.2.0 scope items

| ID | Priority | Scope | Status | Outcome |
|---|---:|---|---|---|
| SANITIZED-EXPORT-001 | P1 | Export/security | Done | Added a sharing-oriented export that excludes authentication, admin, settings, and schema-management tables |
| HELP-001 | P1 | Help/Settings | Done | Split diagnostics, path information, protection warnings, and operation notes |
| STYLE-001 | P1 | RBAC/UI | Done | Made viewer/editor/admin role differences visually clearer |
| CRUD-UX-001 | P1 | CRUD/UI | Done | Reorganized CRUD screens around list-first workflows |
| DB-SEC-OPS-001 | P1 | Security/operations | Done | Added DB/backup/export/log protection diagnostics and guidance |
| RELEASE-REPACK-001 | P1 | Release | Done | Rebuilt, repackaged, smoke-tested, and regenerated manifest/checksum after all P1 items |
| DOC-SYNC-001 | P1 | Docs/external ledgers | Done | Synced GitHub docs and external ledgers after rc2 packaging/release |
| STABLE-RELEASE-001 | P1 | Release | Done | Promoted rc2 to stable v0.2.0 with a non-prerelease GitHub Release |

## SANITIZED-EXPORT-001 completion

Implemented and validated on main:

- `app/infrastructure/export_backup.py`
  - Added allowlist-based sanitized JSON export helper.
- `app/application/export_backup_services.py`
  - Added `ExportBackupService.export_sanitized_json()`.
- `app/ui/sanitized_export_ui.py`
  - Added Operations UI hook for `共有用JSON出力`.
- `app/ui/main_window.py`
  - Applies sanitized export UI hook when creating `OperationsTab`.
- `tests/test_sanitized_export.py`
  - Covers allowlisted export tables, service entrypoint, UI action, and idempotency.

Validation:

- `pytest -q`: PASS
- `ruff check .`: PASS
- `black --check .`: PASS
- `mypy app`: PASS

## HELP-001 completion

Implemented and validated on main:

- `app/ui/help_settings_tab.py`
  - Keeps the Help / Settings tab split into `基本情報`, `パス診断`, `保護警告`, and `操作メモ`.
  - Strengthens the protection warning text for SQL dump, shared JSON export, backup/export/log files, and OS-level access control.
  - Adds operation memo guidance for using shared JSON export versus full SQL dump.
- `tests/test_help_settings_tab.py`
  - Covers required Help / Settings sections, path diagnostics, protection warnings, shared JSON guidance, and refresh behavior.

Validation:

- `pytest -q`: PASS
- `ruff check .`: PASS
- `black --check .`: PASS
- `mypy app`: PASS

## STYLE-001 completion

Implemented and validated on main:

- `app/ui/role_visual_identity.py`
  - Adds viewer/editor/admin visual identities, role banner text, and role-specific label styling.
- `app/ui/main_window.py`
  - Adds a role-specific banner above the main tab area.
  - Applies role-specific styling to the status bar login label.
- `tests/test_role_visual_identity.py`
  - Covers role-specific copy, styling metadata, banner creation, and status label styling.
- `tests/test_main_window_smoke.py`
  - Covers the updated role-banner layout and role-specific banner text.

Validation:

- `pytest -q`: PASS
- `ruff check .`: PASS
- `black --check .`: PASS
- `mypy app`: PASS

## CRUD-UX-001 completion

Implemented and validated on main:

- `app/ui/crud_list_first.py`
  - Extends list-first guidance to `名前を管理`, `タイトル/サブタイトル管理`, `タイトルを管理`, `サブタイトルを管理`, and `関連付け`.
  - Ensures the unified title/subtitle tab also applies list-first handling to child title/subtitle editors.
  - Adds workflow hint labels so each CRUD screen communicates `一覧 → 選択 → 編集/操作`.
  - Handles partial title/subtitle child editors safely.
- `tests/test_crud_list_first.py`
  - Covers table movement, unified title/subtitle child editors, relationship workflow guidance, and idempotency.

Validation:

- `pytest -q`: PASS
- `ruff check .`: PASS
- `black --check .`: PASS
- `mypy app`: PASS

## DB-SEC-OPS-001 completion

Implemented and validated on main:

- `app/ui/help_settings_tab.py`
  - Adds `保護対象パス診断` to the existing `保護警告` section.
  - Lists DB file/folder, change log, operations log, backup folder, daily backup folder, CSV export folder, JSON export folder, and SQL dump folder.
  - Shows existence and parent-writable diagnostics while clarifying that write access is not equivalent to access-control hardening.
  - Explicitly prompts OS ACL / BitLocker / EFS / shared-folder permission checks before sharing or external storage.
- `tests/test_help_settings_tab.py`
  - Covers DB/backup/export/log protected-location diagnostics and refresh behavior.

Validation:

- `pytest -q`: PASS
- `ruff check .`: PASS
- `black --check .`: PASS
- `mypy app`: PASS

## RELEASE-REPACK-001 completion

Validated on local Windows environment for rc2:

- `pytest -q`: PASS
- `ruff check .`: PASS
- `black --check .`: PASS
- `mypy app`: PASS
- `scripts/build_exe_windows.ps1`: PASS
- `scripts/package_release_windows.ps1 -ReleaseName v0.2.0-rc2`: PASS
- `scripts/smoke_test_portable_windows.ps1 -ReleaseDir .\release\v0.2.0-rc2`: PASS

## STABLE-RELEASE-001 completion

Validated on local Windows environment for stable v0.2.0:

- `pytest -q`: PASS
- `ruff check .`: PASS
- `black --check .`: PASS
- `mypy app`: PASS
- `scripts/build_exe_windows.ps1`: PASS
- `scripts/package_release_windows.ps1 -ReleaseName v0.2.0`: PASS
- `scripts/smoke_test_portable_windows.ps1 -ReleaseDir .\release\v0.2.0`: PASS
- `gh release create v0.2.0 ...`: PASS
- `gh release view v0.2.0`: PASS
- `gh release view v0.2.0 --json tagName,isPrerelease,assets,url`: PASS

Generated stable artifacts:

- `release/NameVerification-v0.2.0-portable.zip`
- `release/v0.2.0/00_manifest_v0.2.0_20260525.csv`
- `release/v0.2.0/70_release_evidence/checksums_sha256_v0.2.0_20260525.txt`
- `release/v0.2.0/70_release_evidence/validation_log_template_v0.2.0_20260525.txt`

Stable release asset digests:

- `00_manifest_v0.2.0_20260525.csv`: `sha256:fc20a15b667db29fd6b2c3be63822b229c43fc741858190abaa239e3605494ff`
- `checksums_sha256_v0.2.0_20260525.txt`: `sha256:50c8fc9f27ca4b93899f842ee31cdbd56f8e5a3f4e735a10cc22f7844dcfff68`
- `NameVerification-v0.2.0-portable.zip`: `sha256:616c44389453ffc3af86d680f3f34f9387822e7c3aaebfb19c74db036ab5f8ef`
- `validation_log_template_v0.2.0_20260525.txt`: `sha256:f7179b4471811c1746cae7c4793e87dbcf718949406561a2bcc86a734664e840`

Portable smoke runtime confirmed for stable v0.2.0:

- Release name: `v0.2.0`
- Portable root: `tmp/portable_smoke/v0.2.0/extracted/v0.2.0`
- Portable DB: `30_prod_db/nameverification.db`
- Runtime tables: `app_settings`, `schema_migrations`, `user_audit_logs`, `users`
- Change log path: `40_logs/change_logs.jsonl`
- Operations log path: `40_logs/operations_events.jsonl`

## Current final status

No P1 items remain for v0.2.0.

Optional next actions:

1. Run user-level acceptance on stable v0.2.0.
2. Archive or delete rc2 local artifacts after stable release retention is confirmed.
3. Start a new backlog for v0.3.0.

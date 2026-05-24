# 80_v0_2_0_pre_zip_scope_update_20260523.md

## Purpose

Record the scope update made after v0.2.0-rc1 tag/package/smoke.

## Decision

v0.2.0-rc1 was tagged, built, packaged, and smoke-tested successfully, but it is now treated as a checkpoint rather than the final distribution candidate.

The final zip creation flow was deferred until the remaining future-improvement items were completed inside the v0.2.0 scope. Those implementation P1 items are now complete, and v0.2.0-rc2 packaging/smoke has completed successfully.

## Current checkpoint and release candidate

- Previous checkpoint tag: v0.2.0-rc1
- Previous checkpoint status: hold / checkpoint only
- Current release candidate: v0.2.0-rc2
- Build: PASS
- Package: PASS
- Portable smoke: PASS
- Final zip: `release/NameVerification-v0.2.0-rc2-portable.zip`
- Manifest: `release/v0.2.0-rc2/00_manifest_v0.2.0-rc2_20260525.csv`
- Checksums: `release/v0.2.0-rc2/70_release_evidence/checksums_sha256_v0.2.0-rc2_20260525.txt`
- Final rc2 evidence: docs/81_release_final_v0_2_0_rc2_20260525.md

## Items to complete before the next zip

| ID | Priority | Scope | Status | Expected outcome |
|---|---:|---|---|---|
| SANITIZED-EXPORT-001 | P1 | Export/security | Done | Add a sharing-oriented export that excludes authentication, admin, settings, and schema-management tables |
| HELP-001 | P1 | Help/Settings | Done | Split diagnostics, path information, protection warnings, and operation notes |
| STYLE-001 | P1 | RBAC/UI | Done | Make viewer/editor/admin role differences visually clearer |
| CRUD-UX-001 | P1 | CRUD/UI | Done | Reorganize CRUD screens around list-first workflows |
| DB-SEC-OPS-001 | P1 | Security/operations | Done | Add DB/backup/export/log protection diagnostics and guidance |
| RELEASE-REPACK-001 | P1 | Release | Done | Rebuild, repackage, smoke-test, and regenerate manifest/checksum after all P1 items |
| DOC-SYNC-001 | P1 | Docs/external ledgers | In progress | Sync GitHub docs and external ledgers after rc2 packaging |

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

Validated on local Windows environment:

- `pytest -q`: PASS
- `ruff check .`: PASS
- `black --check .`: PASS
- `mypy app`: PASS
- `scripts/build_exe_windows.ps1`: PASS
- `scripts/package_release_windows.ps1 -ReleaseName v0.2.0-rc2`: PASS
- `scripts/smoke_test_portable_windows.ps1 -ReleaseDir .\release\v0.2.0-rc2`: PASS

Generated artifacts:

- `release/NameVerification-v0.2.0-rc2-portable.zip`
- `release/v0.2.0-rc2/00_manifest_v0.2.0-rc2_20260525.csv`
- `release/v0.2.0-rc2/70_release_evidence/checksums_sha256_v0.2.0-rc2_20260525.txt`
- `release/v0.2.0-rc2/70_release_evidence/validation_log_template_v0.2.0-rc2_20260525.txt`

Portable smoke runtime confirmed:

- Release name: `v0.2.0-rc2`
- Portable root: `tmp/portable_smoke/v0.2.0-rc2/extracted/v0.2.0-rc2`
- Portable DB: `30_prod_db/nameverification.db`
- Runtime tables: `app_settings`, `schema_migrations`, `user_audit_logs`, `users`
- Change log path: `40_logs/change_logs.jsonl`
- Operations log path: `40_logs/operations_events.jsonl`

## Tagging policy

Because `v0.2.0-rc1` is already pushed, do not overwrite it.

Recommended new tag:

- `v0.2.0-rc2`

## External ledger update

External ledgers should treat the generated v0.2.0-rc1 zip as a checkpoint and should not mark it as final distribution.

The external ledger source of truth for rc2 will be updated to:

- `Personal_NameVerification_成果物一覧マスター_v1.8_20260525.xlsx`
- `Personal_NameVerification_WBS_工程管理台帳_v20260525_RC2完了反映版.xlsx`
- `Personal_NameVerification_引継ぎマスター_v20260525_RC2完了反映版.xlsx`
- `Personal_NameVerification_新規チャット初回プロンプト_v20260525_RC2完了反映版.md`

## Next action

1. Create and push `v0.2.0-rc2` tag.
2. Optionally create a GitHub Release for `v0.2.0-rc2` and upload zip/checksum/manifest.
3. Clean local generated folders after artifact retention is confirmed.
4. Delete merged/obsolete remote branches.

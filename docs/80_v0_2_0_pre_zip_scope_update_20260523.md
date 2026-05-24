# 80_v0_2_0_pre_zip_scope_update_20260523.md

## Purpose

Record the scope update made after v0.2.0-rc1 tag/package/smoke.

## Decision

v0.2.0-rc1 was tagged, built, packaged, and smoke-tested successfully, but it is now treated as a checkpoint rather than the final distribution candidate.

The final zip creation flow is deferred until the remaining future-improvement items are completed inside the v0.2.0 scope.

## Current checkpoint

- Tag: v0.2.0-rc1
- Build: PASS
- Package: PASS
- Portable smoke: PASS
- Final evidence: docs/79_release_final_v0_2_0_rc1_20260523.md
- Distribution status: hold / checkpoint only

## Items to complete before the next zip

| ID | Priority | Scope | Status | Expected outcome |
|---|---:|---|---|---|
| SANITIZED-EXPORT-001 | P1 | Export/security | Done | Add a sharing-oriented export that excludes authentication, admin, settings, and schema-management tables |
| HELP-001 | P1 | Help/Settings | Done | Split diagnostics, path information, protection warnings, and operation notes |
| STYLE-001 | P1 | RBAC/UI | Implemented / gate pending | Make viewer/editor/admin role differences visually clearer |
| CRUD-UX-001 | P1 | CRUD/UI | Not started | Reorganize CRUD screens around list-first workflows |
| DB-SEC-OPS-001 | P1 | Security/operations | Not started | Add DB/backup/export/log protection diagnostics and guidance |
| RELEASE-REPACK-001 | P1 | Release | Not started | Rebuild, repackage, smoke-test, and regenerate manifest/checksum after all P1 items |
| DOC-SYNC-001 | P1 | Docs/external ledgers | In progress | Sync GitHub docs and external ledgers after each implemented item |

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

## STYLE-001 progress

Implemented on main:

- `app/ui/role_visual_identity.py`
  - Adds viewer/editor/admin visual identities, role banner text, and role-specific label styling.
- `app/ui/main_window.py`
  - Adds a role-specific banner above the main tab area.
  - Applies role-specific styling to the status bar login label.
- `tests/test_role_visual_identity.py`
  - Covers role-specific copy, styling metadata, banner creation, and status label styling.

Pending:

- Local quality gate re-run.

## Tagging policy

Because `v0.2.0-rc1` is already pushed, do not overwrite it.

Recommended next tag after the remaining P1 items are completed:

- `v0.2.0-rc2`

## External ledger update

External ledgers should treat the generated v0.2.0-rc1 zip as a checkpoint and should not mark it as final distribution.

The external ledger source of truth for this decision is:

- `Personal_NameVerification_成果物一覧マスター_v1.4_20260523.xlsx`
- `Personal_NameVerification_WBS_工程管理台帳_v20260523_HELP完了反映版.xlsx`
- `Personal_NameVerification_引継ぎマスター_v20260523_HELP完了反映版.xlsx`
- `Personal_NameVerification_新規チャット初回プロンプト_v20260523_HELP完了反映版.md`

## Next action

Run the local gates for `STYLE-001`:

```powershell
pytest -q
ruff check .
black --check .
mypy app
```

If all pass, mark `STYLE-001` complete and continue to `CRUD-UX-001`.

After all P1 items are complete, create a new tag and regenerate the portable zip.

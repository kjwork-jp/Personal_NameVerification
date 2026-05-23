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

| ID | Priority | Scope | Expected outcome |
|---|---:|---|---|
| SANITIZED-EXPORT-001 | P1 | Export/security | Add a sharing-oriented export that excludes authentication-related data |
| HELP-001 | P1 | Help/Settings | Split diagnostics, path information, protection warnings, and operation notes |
| STYLE-001 | P1 | RBAC/UI | Make viewer/editor/admin role differences visually clearer |
| CRUD-UX-001 | P1 | CRUD/UI | Reorganize CRUD screens around list-first workflows |
| DB-SEC-OPS-001 | P1 | Security/operations | Add DB/backup/export/log protection diagnostics and guidance |
| RELEASE-REPACK-001 | P1 | Release | Rebuild, repackage, smoke-test, and regenerate manifest/checksum after all P1 items |
| DOC-SYNC-001 | P1 | Docs/external ledgers | Sync GitHub docs and external ledgers after each implemented item |

## Tagging policy

Because `v0.2.0-rc1` is already pushed, do not overwrite it.

Recommended next tag after the remaining P1 items are completed:

- `v0.2.0-rc2`

## External ledger update

External ledgers should treat the generated v0.2.0-rc1 zip as a checkpoint and should not mark it as final distribution.

The external ledger source of truth for this decision is:

- `Personal_NameVerification_外部台帳一括更新マスター_v20260523.xlsx`
- `Personal_NameVerification_新規チャット初回プロンプト_v20260523.md`
- `Personal_NameVerification_最終見直しレビュー_v20260523.txt`

## Next action

Start with `SANITIZED-EXPORT-001`, then proceed one item at a time. After each item, run:

```powershell
pytest -q
ruff check .
black --check .
mypy app
```

After all P1 items are complete, create a new tag and regenerate the portable zip.

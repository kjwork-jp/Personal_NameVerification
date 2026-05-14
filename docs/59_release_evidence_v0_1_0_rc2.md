# 59_release_evidence_v0_1_0_rc2.md

## 1. Release summary

- Release: `v0.1.0-rc2`
- Package type: Windows portable release
- Finalized date: 2026-05-15
- Base branch: `main`
- Base state: after PR #124 merge
- Portable package: `release/NameVerification-v0.1.0-rc2-portable.zip`
- ZIP SHA256: `577237D37CBA0964DF1C5CE685DAABD7B4216813018A1E671FEE6041D1DE0CAE`
- Manifest: `release/v0.1.0-rc2/00_manifest_v0.1.0-rc2_20260515.csv`
- Checksums: `release/v0.1.0-rc2/70_release_evidence/checksums_sha256_v0.1.0-rc2_20260515.txt`

## 2. Portable layout

```text
release/v0.1.0-rc2/
├─ 00_readme/
├─ 10_app/
│  └─ NameVerification.exe
├─ 20_config/
├─ 30_prod_db/
│  └─ nameverification.db  # created at first launch
├─ 40_logs/
│  ├─ change_logs.jsonl
│  └─ operations_events.jsonl
├─ 50_backups/
│  ├─ daily/
│  ├─ before_restore/
│  └─ before_import/
├─ 60_exports/
│  ├─ csv/
│  ├─ json/
│  └─ sql/
├─ 70_release_evidence/
├─ 80_drive_upload/
├─ 90_docs/
└─ 99_review/
```

## 3. Validation results

The following checks passed on Windows before final release evidence fixation.

- `pytest -q`
- `ruff check .`
- `black --check .`
- `mypy app`
- `./scripts/build_exe_windows.ps1`
- `./scripts/smoke_test_exe_windows.ps1`
- `./scripts/package_release_windows.ps1 -ReleaseName v0.1.0-rc2`
- `./scripts/smoke_test_portable_release_windows.ps1 -ReleaseName v0.1.0-rc2`

## 4. Package evidence checks

- `release/NameVerification-v0.1.0-rc2-portable.zip` was generated.
- ZIP SHA256 was recorded.
- Manifest file exists.
- Checksums file exists.
- Generated support README filenames are ASCII-only.
- Mojibake/Japanese support filename search returned no rows.
- `release/v0.1.0-rc2/10_app/NameVerification.exe` exists.
- `release/v0.1.0-rc2/30_prod_db/nameverification.db` is created by portable EXE direct launch.
- `release/v0.1.0-rc2/40_logs/change_logs.jsonl` is the portable change log target.
- `release/v0.1.0-rc2/40_logs/operations_events.jsonl` is the portable operations log target.
- Generated `release/`, `dist/`, and `build/` artifacts are ignored by Git and are not tracked.

## 5. Implemented scope included in this release fixation

- Portable release path defaults.
- Portable package generation script.
- ASCII-only support filenames for generated README files.
- Generated release artifacts ignored by Git.
- SQLite database initialization parent-directory creation.
- SQLite `PRAGMA integrity_check` after schema/public ID setup.
- Portable release smoke script for package-relative DB validation.

## 6. External artifact handling

Generated release artifacts are external deliverables. They must not be committed to Git.

Recommended external handoff set:

- `release/NameVerification-v0.1.0-rc2-portable.zip`
- `release/v0.1.0-rc2/00_manifest_v0.1.0-rc2_20260515.csv`
- `release/v0.1.0-rc2/70_release_evidence/checksums_sha256_v0.1.0-rc2_20260515.txt`
- This document

## 7. Remaining release-adjacent backlog

- Final distribution destination decision.
- UAT execution body and evidence capture.
- Non-empty DB import policy.
- SQL import responsibility boundary.
- Future detailed RBAC separation policy.

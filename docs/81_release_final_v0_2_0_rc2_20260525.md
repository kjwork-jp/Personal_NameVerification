# 81_release_final_v0_2_0_rc2_20260525.md

## Final result

- Version: v0.2.0-rc2
- Build: PASS
- Package: PASS
- Portable smoke: PASS
- Final zip: `release/NameVerification-v0.2.0-rc2-portable.zip`
- Portable folder: `release/v0.2.0-rc2`
- Manifest: `release/v0.2.0-rc2/00_manifest_v0.2.0-rc2_20260525.csv`
- Checksums: `release/v0.2.0-rc2/70_release_evidence/checksums_sha256_v0.2.0-rc2_20260525.txt`
- Validation log template: `release/v0.2.0-rc2/70_release_evidence/validation_log_template_v0.2.0-rc2_20260525.txt`

## Quality gates

- `pytest -q`: PASS
- `ruff check .`: PASS
- `black --check .`: PASS
- `mypy app`: PASS

## Build evidence

- `scripts/build_exe_windows.ps1`: PASS
- Python: 3.13.1
- PyInstaller: 6.20.0
- EXE: `dist/NameVerification.exe`

## Package evidence

- `scripts/package_release_windows.ps1 -ReleaseName v0.2.0-rc2`: PASS
- Release package: `release/NameVerification-v0.2.0-rc2-portable.zip`
- Release directory: `release/v0.2.0-rc2`

## Portable smoke evidence

- `scripts/smoke_test_portable_windows.ps1 -ReleaseDir .\release\v0.2.0-rc2`: PASS
- Release name confirmed by smoke: `v0.2.0-rc2`
- Portable root confirmed by smoke: `tmp/portable_smoke/v0.2.0-rc2/extracted/v0.2.0-rc2`
- Portable DB confirmed by smoke: `30_prod_db/nameverification.db`
- Change log path confirmed by smoke: `40_logs/change_logs.jsonl`
- Operations log path confirmed by smoke: `40_logs/operations_events.jsonl`
- Runtime tables confirmed by smoke: `app_settings`, `schema_migrations`, `user_audit_logs`, `users`

## Scope completed before rc2

- `SANITIZED-EXPORT-001`: Done
- `HELP-001`: Done
- `STYLE-001`: Done
- `CRUD-UX-001`: Done
- `DB-SEC-OPS-001`: Done
- `RELEASE-REPACK-001`: Done

## Go / No-Go

- Decision: GO for v0.2.0-rc2 release candidate
- Remaining actions:
  - Create and push tag `v0.2.0-rc2`
  - Optionally create GitHub Release and upload zip/checksum/manifest
  - Clean local generated folders after retaining release artifacts
  - Delete obsolete remote branches after confirming none are needed

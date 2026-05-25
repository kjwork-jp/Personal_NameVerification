# 85_v0_3_0_backlog_initial_20260525.md

## Baseline

- Stable baseline: v0.2.0
- Stable release status: complete
- Required v0.2.0 P1 items: complete
- Next development target: v0.3.0

## Initial backlog

| ID | Priority | Area | Status | Candidate |
|---|---:|---|---|---|
| V030-OPS-001 | P1 | Release | Done | Automate stable release packaging flow |
| V030-OPS-002 | P1 | Release | Not started | Generate release verification checklist |
| V030-TEST-001 | P1 | Test | Done | Add richer portable smoke coverage |
| V030-UX-001 | P1 | UI | Not started | Redesign CRUD screens as native list-first flows |
| V030-SEC-001 | P1 | Security/Ops | Not started | Add optional Windows file-permission diagnostics |
| V030-DOC-001 | P2 | Docs | Not started | Split user manual from release ledger |
| V030-DATA-001 | P2 | Data | Not started | Add sample database generation mode |
| V030-MAINT-001 | P2 | Maintenance | Not started | Review obsolete checkpoint docs |

## V030-OPS-001 completion

Implemented and validated on main:

- `scripts/run_release_windows.ps1`
  - Orchestrates build, package, and portable smoke for a requested release name.
  - Supports optional GitHub Release creation via `-CreateGitHubRelease`.
  - Supports pre-release creation via `-Prerelease`.
  - Checks expected release artifacts after packaging.
- `tests/test_release_script_contract.py`
  - Statically verifies script existence, orchestration order, release artifact checks, and optional GitHub Release support.

Validation:

- `pytest -q`: PASS
- `ruff check .`: PASS
- `black --check .`: PASS
- `mypy app`: PASS

## V030-TEST-001 completion

Implemented and validated on main:

- `scripts/smoke_test_portable_windows.ps1`
  - Expands the portable smoke flow from 9 to 10 steps.
  - Validates portable README files and release name text.
  - Validates runtime directories for DB, logs, backups, and exports.
  - Performs writable-directory probes for runtime output folders.
  - Expands required SQLite bootstrap table checks to include business tables and change logs.
- `tests/test_release_script_contract.py`
  - Adds static contract tests for runtime directories, README release-name checks, all bootstrap tables, and the 10-step smoke flow.

Validation:

- `pytest -q`: PASS
- `ruff check .`: PASS
- `black --check .`: PASS
- `mypy app`: PASS
- `scripts/run_release_windows.ps1 -ReleaseName v0.3.0-smoke-dryrun`: PASS

Dry-run evidence:

- Release name: `v0.3.0-smoke-dryrun`
- Release package: `release/NameVerification-v0.3.0-smoke-dryrun-portable.zip`
- Portable smoke: PASS
- Runtime tables confirmed: `app_settings`, `change_logs`, `name_subtitle_links`, `name_title_links`, `names`, `schema_migrations`, `subtitles`, `titles`, `user_audit_logs`, `users`

## Suggested first iteration

1. V030-UX-001
2. V030-SEC-001
3. V030-OPS-002
4. V030-DOC-001

## Policy

- Keep v0.2.0 as the stable baseline.
- Use a separate branch or direct-main workflow only after deciding the next implementation item.
- Use hotfix scope only if v0.2.0 requires urgent correction.

## Next action

Continue to `V030-UX-001`.

Target:

- Redesign CRUD screens as native list-first flows.
- Avoid large UI rewrites in one step; start with tab-level structure and smoke-safe contract tests.

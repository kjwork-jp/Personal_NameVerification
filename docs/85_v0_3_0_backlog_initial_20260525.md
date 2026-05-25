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
| V030-OPS-002 | P1 | Release | Implemented / Actions pending | Generate release verification checklist |
| V030-TEST-001 | P1 | Test | Done | Add richer portable smoke coverage |
| V030-UX-001 | P1 | UI | Done | Redesign CRUD screens as native list-first flows |
| V030-SEC-001 | P1 | Security/Ops | Done | Add optional Windows file-permission diagnostics |
| V030-DOC-001 | P2 | Docs | Not started | Split user manual from release ledger |
| V030-DATA-001 | P2 | Data | Not started | Add sample database generation mode |
| V030-MAINT-001 | P2 | Maintenance | Review pending | Review obsolete checkpoint docs |

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

## V030-OPS-002 progress

Implemented on main:

- `scripts/generate_release_checklist_windows.ps1`
  - Generates `release_verification_checklist_<release>_<yyyymmdd>.md` under `70_release_evidence`.
  - Verifies release directory, portable zip, manifest, checksum, validation template, and expected package folders.
  - Fails fast if required artifacts are missing.
- `scripts/run_release_windows.ps1`
  - Runs the release verification checklist generator after package and portable smoke.
  - Includes the checklist in optional GitHub Release asset upload.
- `.github/workflows/release-dry-run.yml`
  - Uploads the generated release verification checklist as a dry-run artifact.
- `tests/test_release_script_contract.py`
  - Adds static contract coverage for checklist generation, release workflow integration, and dry-run artifact upload.

Pending:

- GitHub Actions quality gate result.

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

## V030-UX-001 completion

Implemented and validated on main:

- `app/ui/name_management_tab.py`
  - Makes `名前を管理` a native list-first layout.
  - Orders the tab as header, workflow hint, names list, form, actions, and message.
  - Sets `native_list_first_layout`, `has_list_first_layout`, and `has_list_first_hint` properties directly in the tab.
  - Keeps the existing `apply_crud_list_first()` helper compatible and idempotent.
- `tests/test_name_native_list_first_layout.py`
  - Verifies that the names table is natively before the form/actions.
  - Verifies that the helper does not add duplicate legacy hints for the native name tab.
- `tests/test_audit_log_tab_ui.py`
  - Removes timezone-dependent fixed UTC expectations from the audit log datetime test.

Validation:

- `Quality Gates`: PASS
- `pytest`: PASS through Actions
- `ruff`: PASS through Actions
- `black`: PASS through Actions
- `mypy`: PASS through Actions

## V030-SEC-001 completion

Implemented and validated on main:

- `app/ui/help_settings_tab.py`
  - Adds Windows ACL guidance to the existing protected-path diagnostics.
  - Shows `Get-Acl "<path>" | Format-List` examples for PowerShell.
  - Shows `icacls "<path>"` examples for Command Prompt.
  - Clarifies that `parent writable=True` is not proof of ACL hardening.
  - Prompts operators to review Users / Authenticated Users / Everyone read permissions.
- `tests/test_help_settings_tab.py`
  - Verifies that Windows ACL guidance appears in the Help / Settings protection diagnostics.

Validation:

- `Quality Gates`: PASS
- `pytest`: PASS through Actions
- `ruff`: PASS through Actions
- `black`: PASS through Actions
- `mypy`: PASS through Actions

## GitHub Actions policy

- `Quality Gates` is the default automatic CI for code changes.
- `Quality Gates` ignores docs-only updates to avoid noisy checks for minor documentation edits.
- `Windows validation` is manual-only and is used for medium/risky changes or pre-release checks.
- `Windows EXE Build` is manual-only and is used when a distributable EXE/package is needed.
- `Release Dry Run` is manual-only and is used for release-like verification.
- Minor docs updates or low-risk small fixes: rely on GitHub Actions, not local full gates.
- Medium or risky UI/service/database changes: wait for GitHub Actions or run local gates when needed.
- Release candidates and stable releases: run release dry-run / package / portable smoke before publishing.

## Workflow trigger policy

| Workflow | Auto on push/PR | Manual | Purpose |
|---|---:|---:|---|
| Quality Gates | Yes, except docs-only | Yes | pytest / ruff / black / mypy |
| Windows validation | No | Yes | heavy validation plus EXE smoke |
| Windows EXE Build | No | Yes | distributable EXE/package artifact |
| Release Dry Run | No | Yes | release-like build/package/smoke validation |

## Suggested first iteration

1. V030-OPS-002
2. V030-DOC-001
3. V030-DATA-001
4. V030-MAINT-001

## Policy

- Keep v0.2.0 as the stable baseline.
- Use direct-main workflow with GitHub Actions as the default gate for minor updates.
- Use hotfix scope only if v0.2.0 requires urgent correction.

## Next action

Pull the latest commits and check GitHub Actions:

```powershell
git pull
git status
gh run list --limit 5
```

If the latest `Quality Gates` run passes, mark `V030-OPS-002` complete and continue to `V030-DOC-001`.

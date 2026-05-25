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
| V030-OPS-002 | P1 | Release | Done | Generate release verification checklist |
| V030-TEST-001 | P1 | Test | Done | Add richer portable smoke coverage |
| V030-UX-001 | P1 | UI | Done | Redesign CRUD screens as native list-first flows |
| V030-SEC-001 | P1 | Security/Ops | Done | Add optional Windows file-permission diagnostics |
| V030-DOC-001 | P2 | Docs | Not started | Split user manual from release ledger |
| V030-DATA-001 | P2 | Data | Not started | Add sample database generation mode |
| V030-MAINT-001 | P2 | Maintenance | Review pending | Review obsolete checkpoint docs |

## Completed items

### V030-OPS-001

- Added `scripts/run_release_windows.ps1`.
- Release workflow now orchestrates build, package, portable smoke, optional GitHub Release creation, and required artifact checks.
- Validated by local gates before the GitHub Actions policy change.

### V030-TEST-001

- Expanded `scripts/smoke_test_portable_windows.ps1` from 9 to 10 steps.
- Added runtime directory, README, writable-folder, and SQLite bootstrap table checks.
- Release dry-run passed for `v0.3.0-smoke-dryrun`.

### V030-UX-001

- Changed `app/ui/name_management_tab.py` to a native list-first layout.
- Added static/UI contract tests for the native name-management layout.
- `Quality Gates`: PASS.

### V030-SEC-001

- Added Windows ACL guidance to Help / Settings protected-path diagnostics.
- Added `Get-Acl` and `icacls` guidance.
- `Quality Gates`: PASS.

### V030-OPS-002

- Added `scripts/generate_release_checklist_windows.ps1`.
- `scripts/run_release_windows.ps1` now generates a release verification checklist after package and portable smoke.
- `.github/workflows/release-dry-run.yml` uploads the generated checklist as a dry-run artifact.
- `tests/test_release_script_contract.py` covers checklist generation and workflow integration.
- `Quality Gates`: PASS.

## GitHub Actions policy

| Workflow | Auto on push/PR | Manual | Purpose |
|---|---:|---:|---|
| Quality Gates | Yes, except docs-only | Yes | pytest / ruff / black / mypy |
| Windows validation | No | Yes | heavy validation plus EXE smoke |
| Windows EXE Build | No | Yes | distributable EXE/package artifact |
| Release Dry Run | No | Yes | release-like build/package/smoke validation |

## Suggested next items

1. V030-DOC-001
2. V030-DATA-001
3. V030-MAINT-001

## Next action

Pull the latest docs update and continue to `V030-DOC-001`.

# 85_v0_3_0_backlog_initial_20260525.md

## Baseline

- Stable baseline: v0.2.0
- Stable release status: complete
- Required v0.2.0 P1 items: complete
- Next development target: v0.3.0

## Initial backlog

| ID | Priority | Area | Status | Candidate |
|---|---:|---|---|---|
| V030-OPS-001 | P1 | Release | Implemented / gate pending | Automate stable release packaging flow |
| V030-OPS-002 | P1 | Release | Not started | Generate release verification checklist |
| V030-TEST-001 | P1 | Test | Not started | Add richer portable smoke coverage |
| V030-UX-001 | P1 | UI | Not started | Redesign CRUD screens as native list-first flows |
| V030-SEC-001 | P1 | Security/Ops | Not started | Add optional Windows file-permission diagnostics |
| V030-DOC-001 | P2 | Docs | Not started | Split user manual from release ledger |
| V030-DATA-001 | P2 | Data | Not started | Add sample database generation mode |
| V030-MAINT-001 | P2 | Maintenance | Not started | Review obsolete checkpoint docs |

## V030-OPS-001 progress

Implemented on main:

- `scripts/run_release_windows.ps1`
  - Orchestrates build, package, and portable smoke for a requested release name.
  - Supports optional GitHub Release creation via `-CreateGitHubRelease`.
  - Supports pre-release creation via `-Prerelease`.
  - Checks expected release artifacts after packaging.
- `tests/test_release_script_contract.py`
  - Statically verifies script existence, orchestration order, release artifact checks, and optional GitHub Release support.

Pending:

- Local quality gate re-run.

## Suggested first iteration

1. V030-OPS-001
2. V030-TEST-001
3. V030-UX-001
4. V030-SEC-001

## Policy

- Keep v0.2.0 as the stable baseline.
- Use a separate branch or direct-main workflow only after deciding the next implementation item.
- Use hotfix scope only if v0.2.0 requires urgent correction.

## Next action

Run local gates:

```powershell
pytest -q
ruff check .
black --check .
mypy app
```

If all pass, mark `V030-OPS-001` complete and continue to `V030-TEST-001`.

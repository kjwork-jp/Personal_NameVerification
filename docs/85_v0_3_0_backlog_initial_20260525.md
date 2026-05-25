# 85_v0_3_0_backlog_initial_20260525.md

## Baseline

- Stable baseline: v0.2.0
- Stable release status: complete
- Required v0.2.0 P1 items: complete
- Next development target: v0.3.0

## Remaining backlog

| ID | Priority | Area | Status | Candidate |
|---|---:|---|---|---|
| V030-DATA-001 | P2 | Data | Implemented / Actions pending | Add sample database generation mode |
| V030-MAINT-001 | P2 | Maintenance | Review pending | Review obsolete checkpoint docs |

## Completed items summary

- V030-OPS-001: release workflow orchestration added.
- V030-TEST-001: portable smoke coverage expanded.
- V030-UX-001: name management tab changed to native list-first layout.
- V030-SEC-001: Windows ACL guidance added to Help / Settings diagnostics.
- V030-OPS-002: release verification checklist generator added.
- V030-DOC-001: user manuals and release/development ledgers separated.

## V030-DATA-001 progress

- Added `--preset demo` to `scripts/generate_sample_data.py`.
- Demo SQLite mode generates a small UAT/demo DB with business data and demo users.
- Demo CSV mode generates small CSV files for import/export demonstrations.
- Added tests in `tests/test_generate_sample_data_demo.py`.
- Updated README sample data generation commands.

Pending:

- GitHub Actions quality gate result.

## GitHub Actions policy

| Workflow | Auto on push/PR | Manual | Purpose |
|---|---:|---:|---|
| Quality Gates | Yes, except docs-only | Yes | pytest / ruff / black / mypy |
| Windows validation | No | Yes | heavy validation plus EXE smoke |
| Windows EXE Build | No | Yes | distributable EXE/package artifact |
| Release Dry Run | No | Yes | release-like build/package/smoke validation |

## Next action

Pull the latest commits and check GitHub Actions.

# 85_v0_3_0_backlog_initial_20260525.md

## Baseline

- Stable baseline: v0.2.0
- Stable release status: complete
- Required v0.2.0 P1 items: complete
- Next development target: v0.3.0

## Remaining backlog

| ID | Priority | Area | Status | Candidate |
|---|---:|---|---|---|
| V030-DATA-001 | P2 | Data | Not started | Add sample database generation mode |
| V030-MAINT-001 | P2 | Maintenance | Review pending | Review obsolete checkpoint docs |

## Completed items summary

- V030-OPS-001: release workflow orchestration added.
- V030-TEST-001: portable smoke coverage expanded.
- V030-UX-001: name management tab changed to native list-first layout.
- V030-SEC-001: Windows ACL guidance added to Help / Settings diagnostics.
- V030-OPS-002: release verification checklist generator added.
- V030-DOC-001: user manuals and release/development ledgers separated.

## V030-DOC-001 completion

- Added `docs/manuals/00_user_manual_index.md` as the user-facing document entry point.
- Added `docs/release_ledger/00_release_ledger_index.md` as the release/development ledger entry point.
- Updated `README.md` to route users to manuals and developers/release operators to ledgers.
- This was docs-only and did not require local quality gates.

## GitHub Actions policy

| Workflow | Auto on push/PR | Manual | Purpose |
|---|---:|---:|---|
| Quality Gates | Yes, except docs-only | Yes | pytest / ruff / black / mypy |
| Windows validation | No | Yes | heavy validation plus EXE smoke |
| Windows EXE Build | No | Yes | distributable EXE/package artifact |
| Release Dry Run | No | Yes | release-like build/package/smoke validation |

## Next action

Pull the latest docs update and continue to `V030-DATA-001`.

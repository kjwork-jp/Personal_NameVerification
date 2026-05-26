# 85_v0_3_0_backlog_initial_20260525.md

## Baseline

- Stable baseline: v0.2.0
- Stable release status: complete
- Required v0.2.0 P1 items: complete
- Current development line: v0.3.0+
- Latest `Quality Gates`: pass for `fix: wrap title subtitle layout assertions` / run `26426351458`

## Backlog references

| Scope | Document |
|---|---|
| Immediate v0.3.x work | this file |
| Future roadmap / remaining backlog | `docs/86_future_roadmap_and_remaining_backlog_20260525.md` |
| UAT execution plan | `docs/91_uat_execution_plan_20260526.md` |
| UAT checklist | `docs/92_uat_checklist_20260526.md` |
| UAT execution record | `docs/93_uat_execution_record_20260526.md` |
| Large data performance review | `docs/88_large_data_performance_review_20260525.md` |
| Asset storage and relative path policy | `docs/89_asset_storage_and_relative_path_policy_20260525.md` |
| Local SQLite / multi-user policy | `docs/90_local_sqlite_single_user_and_multi_user_policy_20260525.md` |
| Document maintenance review | `docs/87_doc_maintenance_review_20260525.md` |
| Open issues / constraints | `docs/97_open_issues_and_constraints.md` |
| Release/development ledger index | `docs/release_ledger/00_release_ledger_index.md` |

## Execution policy

- Implementation / documentation / maintenance backlog is complete for this ledger window.
- UAT preparation is complete enough to begin local execution.
- Release preparation remains deferred until UAT is complete and release blockers are cleared.
- Release-like scripts and CI definitions can still be maintained, but publishing/release preparation is not immediate work unless explicitly selected.

## Immediate remaining backlog

No active implementation / documentation / maintenance backlog remains in this ledger window.

## Deferred gates

| ID | Horizon | Priority | Area | Status | Candidate |
|---|---|---:|---|---|---|
| V900-UAT-001 | post-backlog | P1 | UAT | Ready for local execution | Run demo DB based UAT for viewer/editor/admin flows |
| V100-REL-001 | post-UAT | P1 | Release | Deferred until UAT complete | Prepare v1.0 release criteria, final UAT, and distribution policy |

## Completed items summary

- V030-OPS-001: release workflow orchestration added.
- V030-TEST-001: portable smoke coverage expanded.
- V030-UX-001: name management tab changed to native list-first layout.
- V030-SEC-001: Windows ACL guidance added to Help / Settings diagnostics.
- V030-OPS-002: release verification checklist generator added.
- V030-DOC-001: user manuals and release/development ledgers separated.
- V030-DATA-001: demo sample SQLite/CSV generation mode added.
- V030-MAINT-001: docs maintenance review ledger added; no files deleted.
- V030-DOC-002: existing manuals refreshed for latest tabs, RBAC, data operations, and deferral policy.
- V030-UX-002: title/subtitle management native list-first layout and tests.
- V030-OPS-003: Windows EXE workflow artifact alignment and static contract tests.
- V040-EXPORT-001: sanitized JSON export excludes `change_logs` and non-application/admin tables.
- V040-IMPORT-001: CSV/JSON import source preview diagnostics added.
- V040-AUDIT-001: operation history review JSON export added.
- V040-SEC-001: operator file protection checklist added to Help / Settings.
- V040-UX-001: structured role capability summary added.
- V050-PERF-001: large data performance review plan and bulk generator contract tests added.
- V050-ASSET-001: asset storage and relative path policy documented.
- V050-MULTI-001: local SQLite single-user and future multi-user policy documented.

## V900-UAT-001 preparation

- Added `docs/91_uat_execution_plan_20260526.md`.
- Added `docs/92_uat_checklist_20260526.md`.
- Added `docs/93_uat_execution_record_20260526.md`.
- UAT execution has not been recorded yet.
- Release remains deferred.

## Quality gate closure

- `Quality Gates` passed for latest fix commit after ruff E501 corrections.
- Previous failing runs were superseded by the passing run.
- No generated DB/CSV data was committed.

## GitHub Actions policy

| Workflow | Auto on push/PR | Manual | Purpose |
|---|---:|---:|---|
| Quality Gates | Yes, except docs-only | Yes | pytest / ruff / black / mypy |
| Windows validation | No | Yes | heavy validation plus EXE smoke |
| Windows EXE Build | No | Yes | distributable EXE/package artifact |
| Release Dry Run | No | Yes | release-like build/package/smoke validation |

## Next action

Run the local UAT setup commands in `docs/93_uat_execution_record_20260526.md`, then execute the checklist in `docs/92_uat_checklist_20260526.md`. Release preparation remains deferred until UAT is complete.

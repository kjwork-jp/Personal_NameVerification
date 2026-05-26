# 86_future_roadmap_and_remaining_backlog_20260525.md

## Purpose

This document tracks the remaining backlog and future expansion items after the v0.3.0 initial backlog cleanup.

It intentionally includes more than the immediate P2 items so that deferred UAT/release gates remain visible after implementation work is completed.

## Current baseline

- Stable baseline: v0.2.0
- Current development line: v0.3.0+
- Main short backlog: `docs/85_v0_3_0_backlog_initial_20260525.md`
- Open issue source: `docs/97_open_issues_and_constraints.md`
- Latest `Quality Gates`: pass for `fix: wrap title subtitle layout assertions` / run `26426351458`

## Execution policy

- Implementation / documentation / maintenance backlog is complete for this roadmap window.
- UAT is the next gate, but release preparation remains deferred until UAT is complete.
- Continue small direct-main changes with GitHub Actions as the default quality gate.
- Release-like validation scripts can be maintained before release, but publishing/release preparation stays deferred unless explicitly selected.

## Remaining backlog / future roadmap

| ID | Horizon | Priority | Area | Status | Candidate |
|---|---|---:|---|---|---|
| V900-UAT-001 | post-backlog | P1 | UAT | Ready / deferred gate | Run demo DB based UAT for viewer/editor/admin flows |
| V100-REL-001 | post-UAT | P1 | Release | Deferred until UAT complete | Prepare v1.0 release criteria, final UAT, and distribution policy |

## Completed in this roadmap window

- V030-MAINT-001: document maintenance review ledger added; no files deleted.
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

## Quality gate closure

- Latest Quality Gates passed after ruff E501 fixes.
- Earlier failing workflow runs are superseded by the passing run.
- No generated DB/CSV data was committed.

## Immediate next items

1. Decide whether to start `V900-UAT-001`.
2. Keep `V100-REL-001` deferred until UAT is complete.
3. If more implementation work is found during UAT, route it back into a new backlog before release preparation.

## Deferred gates

| ID | Gate | Trigger |
|---|---|---|
| V900-UAT-001 | UAT | Can start now if formal UAT is selected. |
| V100-REL-001 | Release | Start only after UAT is complete and all release blockers are cleared. |

## Maintenance review policy

For obsolete checkpoint documents, do not delete first.
Classify each document as one of the following:

| Classification | Meaning | Action |
|---|---|---|
| keep | Still current or source-of-truth relevant | Keep as-is or link from index |
| archive candidate | Historical but useful for traceability | Move/link under release ledger or mark archived |
| obsolete candidate | Superseded and not needed for normal reference | List before deletion; delete only after explicit approval |
| merge candidate | Useful content exists but file can be consolidated | Merge into current ledger/manual then archive |

## Notes

- This file is a planning ledger.
- UAT and release remain separate gates.
- Release-like validation scripts can be maintained before release, but publishing/release preparation stays deferred.

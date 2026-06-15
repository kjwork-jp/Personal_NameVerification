# 86_future_roadmap_and_remaining_backlog_20260525.md

## Purpose

This document tracks the remaining backlog and future expansion items after the v0.3.0 initial backlog cleanup.

UAT and release publishing are **explicitly selected deferred gates** and are not normal active backlog items.

## Current baseline

- Stable baseline: v0.2.0
- Current development line: v0.3.0+
- Main short backlog: `docs/85_v0_3_0_backlog_initial_20260525.md`
- Open issue source: `docs/97_open_issues_and_constraints.md`
- Latest `Quality Gates`: success for PR #184 exact head and merge commit `325244defdf9658f5ea16c9550fcd73d8c5aefc6` (run `27526922774`)
- Current open PR: #185 (as of 2026-06-15)

## Execution policy

- Implementation / documentation / maintenance backlog is complete for this roadmap window.
- Manual UAT, EXE checks, portable checks, local Windows builds, and release publishing are **not** normal active backlog items.
- Continue small direct-main changes with GitHub Actions as the default quality gate.
- Release-like validation scripts can be maintained before release, but publishing/release preparation stays deferred unless explicitly selected.

## Current confirmed design candidates (P2)

These are confirmed design candidates for the v0.3.0+ line, audited against current code/tests:

| ID | Candidate | Status |
|---|---|---|
| UI-DESIGN-01 | list columns reduction + detail pane | design candidate |
| UI-DESIGN-02 | subtitle-first editing | design candidate |
| UI-DESIGN-03 | search single table + detail pane | design candidate |

These are design candidates, not confirmed defects. Implementation should be based on current code/tests/screenshots, not on old handoff references.

## Explicitly selected deferred gates

These gates are intentionally deferred and are NOT active backlog items to be automatically progressed.

| ID | Gate | Status | Trigger |
|---|---|---|---|
| V900-UAT-001 | Manual UAT (viewer/editor/admin flows) | Deferred explicit gate | Requires explicit human decision to start |
| V100-REL-001 | Release preparation (criteria, tagging, packaging, distribution) | Deferred explicit gate | Requires explicit human decision; not automated next step |

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
- PR #184: `feat: enforce normalized display-name indexes` merged (squash, merge commit `325244defdf9658f5ea16c9550fcd73d8c5aefc6`)

## Quality gate closure

- Latest Quality Gates: success for PR #184 merge (run `27526922774`)
- PR #185 exact-head Quality Gates: run `27537532720` / pytest 7 failures, ruff/black/mypy success (pending resolution)
- No generated DB/CSV data was committed.

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
- UAT and release are explicitly deferred gates (see section above); they are not sequenced as automatic next steps.
- Release-like validation scripts can be maintained before release, but publishing/release preparation stays deferred.

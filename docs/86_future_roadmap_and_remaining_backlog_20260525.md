# 86_future_roadmap_and_remaining_backlog_20260525.md

## Purpose

This document tracks the remaining backlog and future expansion items after the v0.3.0 initial backlog cleanup.

It intentionally includes more than the immediate P2 items so that the remaining work does not disappear when a short backlog is completed.

## Current baseline

- Stable baseline: v0.2.0
- Current development line: v0.3.0+
- Main short backlog: `docs/85_v0_3_0_backlog_initial_20260525.md`
- Open issue source: `docs/97_open_issues_and_constraints.md`

## Execution policy

- Do not start UAT until the implementation / documentation / maintenance backlog is completed.
- Do not start release preparation until all active backlog items are completed and reviewed.
- UAT and release items remain tracked here, but they are deferred gates, not immediate work.
- Continue small direct-main changes with GitHub Actions as the default quality gate.

## Remaining backlog / future roadmap

| ID | Horizon | Priority | Area | Status | Candidate |
|---|---|---:|---|---|---|
| V030-UX-002 | v0.3.x | P2 | UI | Implemented / Actions pending | Extend native list-first layout beyond name management |
| V030-OPS-003 | v0.3.x | P2 | CI/Release | Implemented / Actions pending | Verify manual-only heavy workflows and release dry-run artifact definitions without publishing |
| V040-EXPORT-001 | v0.4.x | P2 | Data/Security | Implemented / Actions pending | Expand sanitized application-data-only export policy and tests |
| V040-IMPORT-001 | v0.4.x | P2 | Data/Ops | Implemented / Actions pending | Improve import validation, preview, and rollback evidence |
| V040-AUDIT-001 | v0.4.x | P2 | Audit | Implemented / Actions pending | Strengthen audit log review/export workflow for operations |
| V040-SEC-001 | v0.4.x | P2 | Security/Ops | Implemented / Actions pending | Add deeper OS file protection guidance and operator checklist |
| V040-UX-001 | v0.4.x | P2 | UI | Implemented / Actions pending | Improve role-specific visual cues and dashboard readability |
| V050-PERF-001 | v0.5.x | P3 | Performance | Implemented / Actions pending | Re-check large data performance and table pagination/search behavior |
| V050-ASSET-001 | v0.5.x | P3 | Assets | Implemented / docs-only | Revisit icon/image asset storage and relative path handling |
| V050-MULTI-001 | v0.5.x | P3 | Architecture | Implemented / docs-only | Revisit single-user/local SQLite constraints before multi-user use |
| V900-UAT-001 | post-backlog | P1 | UAT | Deferred until all backlog complete | Run demo DB based UAT for viewer/editor/admin flows |
| V100-REL-001 | post-UAT | P1 | Release | Deferred until all backlog complete | Prepare v1.0 release criteria, final UAT, and distribution policy |

## Completed in this roadmap window

- V030-MAINT-001: document maintenance review ledger added; no files deleted.
- V030-DOC-002: existing manuals refreshed for latest tabs, RBAC, data operations, and deferral policy.
- V050-ASSET-001: asset storage and relative path policy documented.
- V050-MULTI-001: local SQLite single-user and future multi-user policy documented.

## Immediate next items

1. Check GitHub Actions for implemented code changes.
2. Mark Actions-pending implementation items done if `Quality Gates` passes.
3. Keep UAT and Release deferred until all backlog work is complete.

## Deferred gates

| ID | Gate | Trigger |
|---|---|---|
| V900-UAT-001 | UAT | Start only after implementation / documentation / maintenance backlog is complete. |
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

- This file is a planning ledger. It does not imply all candidates must be implemented before the next release.
- Immediate v0.3.x items are expected to stay small and low-risk unless explicitly promoted.
- Release-like validation scripts can be maintained before release, but publishing/release preparation stays deferred.

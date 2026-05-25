# 85_v0_3_0_backlog_initial_20260525.md

## Baseline

- Stable baseline: v0.2.0
- Stable release status: complete
- Required v0.2.0 P1 items: complete
- Current development line: v0.3.0+

## Backlog references

| Scope | Document |
|---|---|
| Immediate v0.3.x work | this file |
| Future roadmap / remaining backlog | `docs/86_future_roadmap_and_remaining_backlog_20260525.md` |
| Document maintenance review | `docs/87_doc_maintenance_review_20260525.md` |
| Open issues / constraints | `docs/97_open_issues_and_constraints.md` |
| Release/development ledger index | `docs/release_ledger/00_release_ledger_index.md` |

## Execution policy

- UAT is deferred until the implementation / documentation / maintenance backlog is complete.
- Release preparation is deferred until UAT is complete and release blockers are cleared.
- Release-like scripts and CI definitions can still be maintained, but publishing/release preparation is not immediate work.

## Immediate remaining backlog

| ID | Priority | Area | Status | Candidate |
|---|---:|---|---|---|
| V030-MAINT-001 | P2 | Maintenance | Implemented / review pending | Review obsolete checkpoint docs |
| V030-UX-002 | P2 | UI | Candidate | Extend native list-first layout beyond name management |
| V030-DOC-002 | P2 | Docs | Candidate | Refresh existing manuals to match latest tabs/RBAC/data operations |
| V030-OPS-003 | P2 | CI/Release | Candidate | Verify manual-only heavy workflows and release dry-run artifact definitions without publishing |
| V040-EXPORT-001 | P2 | Data/Security | Candidate | Expand sanitized application-data-only export policy and tests |

## Later roadmap snapshot

| ID | Horizon | Priority | Area | Status | Candidate |
|---|---|---:|---|---|---|
| V040-IMPORT-001 | v0.4.x | P2 | Data/Ops | Candidate | Improve import validation, preview, and rollback evidence |
| V040-AUDIT-001 | v0.4.x | P2 | Audit | Candidate | Strengthen audit log review/export workflow for operations |
| V040-SEC-001 | v0.4.x | P2 | Security/Ops | Candidate | Add deeper OS file protection guidance and operator checklist |
| V040-UX-001 | v0.4.x | P2 | UI | Candidate | Improve role-specific visual cues and dashboard readability |
| V050-PERF-001 | v0.5.x | P3 | Performance | Candidate | Re-check large data performance and table pagination/search behavior |
| V050-ASSET-001 | v0.5.x | P3 | Assets | Candidate | Revisit icon/image asset storage and relative path handling |
| V050-MULTI-001 | v0.5.x | P3 | Architecture | Candidate | Revisit single-user/local SQLite constraints before multi-user use |
| V900-UAT-001 | post-backlog | P1 | UAT | Deferred until all backlog complete | Run demo DB based UAT for viewer/editor/admin flows |
| V100-REL-001 | post-UAT | P1 | Release | Deferred until all backlog complete | Prepare v1.0 release criteria, final UAT, and distribution policy |

## Completed items summary

- V030-OPS-001: release workflow orchestration added.
- V030-TEST-001: portable smoke coverage expanded.
- V030-UX-001: name management tab changed to native list-first layout.
- V030-SEC-001: Windows ACL guidance added to Help / Settings diagnostics.
- V030-OPS-002: release verification checklist generator added.
- V030-DOC-001: user manuals and release/development ledgers separated.
- V030-DATA-001: demo sample SQLite/CSV generation mode added.

## V030-MAINT-001 progress

- Added `docs/87_doc_maintenance_review_20260525.md`.
- Classified current docs into keep / archive candidate / obsolete candidate / merge candidate.
- No files were deleted.
- Obsolete candidates are not approved for deletion yet.
- Follow-up work routes to `V030-DOC-002`, `V030-UX-002`, and future roadmap items.

## GitHub Actions policy

| Workflow | Auto on push/PR | Manual | Purpose |
|---|---:|---:|---|
| Quality Gates | Yes, except docs-only | Yes | pytest / ruff / black / mypy |
| Windows validation | No | Yes | heavy validation plus EXE smoke |
| Windows EXE Build | No | Yes | distributable EXE/package artifact |
| Release Dry Run | No | Yes | release-like build/package/smoke validation |

## Next action

Review `docs/87_doc_maintenance_review_20260525.md`. If acceptable, mark `V030-MAINT-001` done and continue to `V030-UX-002`.

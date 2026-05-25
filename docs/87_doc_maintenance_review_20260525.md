# 87_doc_maintenance_review_20260525.md

## Purpose

This document classifies existing planning, release, checklist, and historical documents without deleting them.

Deletion is intentionally out of scope. Any delete action requires a separate explicit approval after this review.

## Classification rules

| Classification | Meaning | Action |
|---|---|---|
| keep | Still current or source-of-truth relevant | Keep as-is or link from an index |
| archive candidate | Historical but useful for traceability | Keep, but treat as historical/release evidence |
| obsolete candidate | Superseded and not needed for normal reference | List only; delete only after explicit approval |
| merge candidate | Useful content exists but file can be consolidated | Merge useful content into current ledger/manual, then archive |

## Current source-of-truth documents

| File | Classification | Reason | Action |
|---|---|---|---|
| `README.md` | keep | Current repository entry point | Keep |
| `docs/manuals/00_user_manual_index.md` | keep | User-facing manual entry point | Keep |
| `docs/release_ledger/00_release_ledger_index.md` | keep | Release/development ledger entry point | Keep |
| `docs/85_v0_3_0_backlog_initial_20260525.md` | keep | Immediate v0.3.x backlog | Keep |
| `docs/86_future_roadmap_and_remaining_backlog_20260525.md` | keep | Future roadmap and remaining backlog | Keep |
| `docs/87_doc_maintenance_review_20260525.md` | keep | Current maintenance review ledger | Keep |
| `docs/97_open_issues_and_constraints.md` | merge candidate | Contains older open issues plus many resolved items | Merge still-relevant constraints into `docs/86`, then archive |

## Release evidence / historical checkpoints

| File | Classification | Reason | Action |
|---|---|---|---|
| `docs/83_release_final_v0_2_0_20260525.md` | archive candidate | Stable v0.2.0 final release evidence | Keep under release ledger reference |
| `docs/81_release_final_v0_2_0_rc2_20260525.md` | archive candidate | rc2 historical evidence | Keep as historical checkpoint |
| `docs/80_v0_2_0_pre_zip_scope_update_20260523.md` | archive candidate | v0.2.0 pre-zip scope history | Keep as historical checkpoint |
| `docs/78_release_evidence_v0_2_0_rc1.md` | archive candidate | rc1 historical evidence | Keep as historical checkpoint |
| `docs/59_release_evidence_v0_1_0_rc2.md` | archive candidate | v0.1.0-rc2 historical evidence | Keep as historical checkpoint |

## Planning / design documents

| File | Classification | Reason | Action |
|---|---|---|---|
| `docs/75_v0_2_0_current_status_and_improvement_ledger.md` | archive candidate | v0.2.0 status source, now mostly superseded by v0.3.x ledgers | Keep as historical source |
| `docs/74_rbac_hardening_plan.md` | archive candidate | RBAC hardening mostly implemented, still useful for traceability | Keep |
| `docs/73_ui_navigation_redesign_plan.md` | merge candidate | Still relevant for future list-first/UI work | Merge remaining items into `V030-UX-002` / `V040-UX-001` |
| `docs/72_v0_2_0_auth_integrated_uat_execution_record.md` | archive candidate | Historical UAT execution record | Keep as historical evidence |
| `docs/71_v0_2_0_auth_integrated_uat_checklist.md` | archive candidate | Historical UAT checklist; UAT is now deferred | Keep, do not use as immediate work item |
| `docs/70_v0_2_0_auth_user_management_implementation_plan.md` | archive candidate | v0.2.0 auth implementation plan mostly completed | Keep as historical source |
| `docs/69_v0_2_0_design_completeness_review.md` | merge candidate | Some design gaps may still inform v0.4+ | Merge remaining gaps into roadmap before archiving |
| `docs/68_database_file_protection_policy.md` | keep | Still relevant for OS/file protection policy | Keep and link from security docs |
| `docs/67_quality_attribute_gap_analysis.md` | merge candidate | Useful quality gaps may map to v0.4/v0.5 | Merge remaining items into roadmap |
| `docs/66_security_user_management_gap_analysis.md` | archive candidate | Security/user gaps mostly implemented in v0.2.x | Keep as historical source |
| `docs/65_readonly_rbac_future_policy.md` | merge candidate | Role-specific behavior still relevant | Merge into future RBAC/UX roadmap |
| `docs/64_data_scale_and_asset_storage_policy.md` | keep | Still relevant for performance/assets roadmap | Keep |
| `docs/63_distribution_and_uat_plan.md` | archive candidate | Historical distribution/UAT planning; UAT is deferred | Keep as historical, not immediate work |

## Manuals

| File | Classification | Reason | Action |
|---|---|---|---|
| `docs/manuals/NameVerification_初回教育用_簡易マニュアル.md` | merge candidate | User-facing but may need latest tab/RBAC updates | Refresh under `V030-DOC-002` |
| `docs/manuals/NameVerification_運用操作マニュアル_機能説明.md` | merge candidate | User-facing but may need latest tab/RBAC/data operation updates | Refresh under `V030-DOC-002` |
| `docs/manuals/NameVerification_運用手順書_詳細版.md` | merge candidate | Operationally useful but likely needs latest release/dry-run policy alignment | Refresh under `V030-DOC-002` |

## Obsolete candidates

No immediate deletion candidates are approved.

Potential obsolete candidates should only be identified after merge-candidate content is reviewed and migrated.

## Maintenance outcome

- No files deleted.
- Current entry points are clarified.
- Historical release evidence remains preserved.
- Future-relevant items are routed to the roadmap instead of being lost.
- Manual refresh remains tracked as `V030-DOC-002`.
- UI follow-up remains tracked as `V030-UX-002` / `V040-UX-001`.
- UAT and release remain deferred until all backlog work is complete.

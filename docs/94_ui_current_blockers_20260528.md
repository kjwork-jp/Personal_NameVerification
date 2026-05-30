# 94_ui_current_blockers_20260528.md

## 1. Current status

This document is synchronized with the final UAT evidence recorded in:

- `docs/96_final_uat_evidence_20260530.md`

The previously listed blockers are no longer active release blockers for the observed UAT scope.

## 2. Resolved / accepted items

| ID | Type | Current status | Evidence / note |
|---|---|---|---|
| QG-RUFF-001 | Quality Gate | RESOLVED | Latest confirmed implementation Quality Gates are green: `138c15321845f56a756124e1fc9978446e23a5fb` / run `26660843878`. |
| UI-SUBTITLE-LIST-001 | UI bug | UAT PASS | Screenshot UAT shows subtitle-specific rows and columns, not title rows. |
| UI-SUBTITLE-PARENT-001 | UI readability | UAT PASS | Parent title is split into title name, public ID, and state. |
| UI-SUBTITLE-FLOW-001 | UX flow | UAT PASS | Edit/delete screenshots show concrete selected subtitle targets. |
| UI-TABLE-001 | Common UI | ACCEPTED FOR CURRENT UAT | Readability is sufficient for the observed release-critical scope. Broader table polish remains follow-up. |
| UI-AUDIT-001 | Audit UI | UAT PASS FOR DISPLAY | Pretty/diff-style audit display is visible in screenshots. Audit export evidence is optional unless release policy requires it. |
| UI-LOGIN-001 | Login UI | UAT PASS | Login screen and role context are visible. |
| UI-DATAIO-001 | Data I/O UI | UAT PASS | Guide, group descriptions, result hint, `[OK] CSV export 成功`, and Operations Log guidance are visible. |
| SUBTITLE-ROW-COUNT-SPEC | Subtitle Management | ACCEPTED SPEC | Edit/delete candidate list is scoped to the selected parent title. Four rows under `sample-title-0000017` are valid for the observed parent-scoped behavior. Cross-parent editing/search is a future enhancement if requested. |

## 3. Remaining release blockers

| ID | Status | Details |
|---|---|---|
| None | CLOSED | No active release blocker remains in this document for the observed final UAT scope. |

## 4. Follow-up backlog, not release blockers

| ID | Priority | Scope | Treatment |
|---|---:|---|---|
| AUDIT-EXPORT-EVIDENCE-OPTIONAL | P2 | Capture explicit audit export evidence. | Optional unless release policy requires export evidence. |
| CROSS-PARENT-SUBTITLE-SEARCH | P2 | Search/edit subtitles across all parent titles. | Enhancement only. Current release accepts parent-scoped candidate lists. |
| UI-POLISH-FOLLOWUP | P2/P3 | Broader design-system, navigation, empty-state, keyboard, copy, and accessibility polish. | Follow-up backlog, not current release blocker. |

## 5. Release decision dependency

Release readiness now depends on the final release decision document/status, not on unresolved blockers in this file.

Recommended next step:

1. Record final release readiness decision.
2. If release-ready, keep optional items as follow-up backlog.
3. If blocked later, create new explicit defect IDs instead of reopening historical blocker rows.

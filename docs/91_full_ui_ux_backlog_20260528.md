# 91_full_ui_ux_backlog_20260528.md

## 1. Purpose

This document is the historical full UI/UX backlog for Personal_NameVerification.

As of the 2026-05-30 final UAT evidence update, this file is no longer the active open-blocker list. It is synchronized here to show which items were implemented, which were validated, and which future polish items remain optional or follow-up scope.

Active final evidence is recorded in:

- `docs/95_next_phase_workplan_20260530.md`
- `docs/96_final_uat_evidence_20260530.md`

## 2. Current synchronized baseline

| Area | Current state |
|---|---|
| Quality Gates | Latest confirmed implementation Quality Gates are green: `138c15321845f56a756124e1fc9978446e23a5fb` / `chatgpt/quality-gates` success / run `26660843878`. |
| Login | PASS in screenshot UAT. Windows/local authentication sections and role context are visible. |
| Subtitle management | PASS in screenshot UAT. Subtitle list is subtitle-specific, parent-title info is split, and edit/delete selected targets are visible. |
| Subtitle row count | PASS / SPEC NOTE. Edit/delete candidate rows are scoped to the selected parent title. Four rows for `sample-title-0000017` are treated as valid for parent-scoped behavior. |
| Data I/O | PASS in screenshot UAT. Guide header, operation descriptions, result hint, `[OK] CSV export 成功`, and Operations Log guidance are visible. |
| Audit | PASS for display UAT. Pretty/diff-style sections are visible. Audit export evidence remains optional unless release policy requires it. |
| Release evidence | `docs/96_final_uat_evidence_20260530.md` updated from `スクリーンショット 2026-05-30 070948.zip` and `スクリーンショット 2026-05-30 085030.zip`. |
| Release readiness | Pending final decision after this backlog and current blockers document are synchronized. |

## 3. Priority definitions

| Priority | Meaning |
|---|---|
| P0 | Blocks validation or release decision. Must be closed or explicitly accepted. |
| P1 | Required for release confidence or clear user operation. |
| P2 | Quality improvement; can become follow-up if not release blocking. |
| P3 | Polish / future hardening. Not a blocker when evidence-based release readiness is explicitly accepted. |

## 4. Synchronized backlog status

### 4.1 P0 / P1 items

| ID | Area | Previous problem | Current status | Evidence / note |
|---|---|---|---|---|
| QG-RUFF-001 | Quality Gates | Previous subtitle-list fix failed ruff. | RESOLVED | Quality Gates restored and latest implementation baseline is green. |
| UI-SUBTITLE-LIST-001 | Subtitle Management / List | List displayed title rows / inherited title table semantics. | UAT PASS | Screenshot UAT shows subtitle-specific columns and rows. |
| UI-SUBTITLE-LIST-002 | Subtitle Management / List | Refresh was fragile and not clearly tied to create/update. | ACCEPTED FOR CURRENT UAT | No current UAT blocker recorded. Keep as follow-up only if refresh defects reappear. |
| UI-SUBTITLE-PARENT-001 | Subtitle Management | Parent title display was one dense line. | UAT PASS | Parent title is split into title name, public ID, and state. |
| UI-SUBTITLE-FLOW-001 | Subtitle Management | Add/edit/delete target was hard to understand. | UAT PASS | Edit/delete screenshots show selected subtitle targets. |
| UI-SUBTITLE-SEARCH-001 | Subtitle Management | Search behavior needed to be usable. | ACCEPTED FOR CURRENT UAT | Parent-scoped behavior is accepted. Cross-parent editing/search is future enhancement if requested. |
| UI-SUBTITLE-EDIT-001 | Subtitle Management | Editing depended on implicit selection. | UAT PASS | Selected subtitle summary is visible after row selection. |
| UI-TITLE-EDIT-001 | Title Management | Edit layout was sparse/awkward. | NOT IN FINAL BLOCKER SET | No current blocker evidence in final UAT bundle. Treat as future polish unless new defect is reported. |
| UI-TITLE-CONTEXT-001 | Title Management | Selected title context was verbose. | PARTIALLY ADDRESSED | Subtitle parent-title summary is improved. Broader title-management polish is future scope. |
| UI-TABLE-001 | Common Tables | Tables were dense and mechanical. | PARTIALLY ADDRESSED / ACCEPTED | Subtitle, audit, and related operational screens are readable enough for current UAT. |
| UI-ID-001 | Common IDs | UUIDs dominated screen space. | PARTIALLY ADDRESSED | Parent title/public ID fields are separated. Full UUID reduction remains future polish. |
| UI-LOGIN-001 | Login | Login window was too plain. | UAT PASS | Windows/local authentication sections and role context are visible. |
| UI-ROLE-001 | RBAC | Role differences were not clear enough. | UAT PASS FOR OBSERVED SCOPE | Role context is visible after login. |
| DOC-STATUS-001 | Docs | Status docs needed synchronization. | IN PROGRESS | docs/91 and docs/94 are being synchronized; docs/96 is current evidence. |

### 4.2 P2 / P3 items

| ID | Area | Status | Release treatment |
|---|---|---|---|
| UI-NAV-001 | Main Navigation | FOLLOW-UP | Not release blocking based on current UAT evidence. |
| UI-COLOR-001 | Visual Design | FOLLOW-UP | Not release blocking unless new UAT defect is reported. |
| UI-FORM-001 | Forms | PARTIALLY ADDRESSED | Current critical flows are readable; broader standardization is future scope. |
| UI-EMPTY-001 | Empty State | FOLLOW-UP | Not release blocking based on current evidence. |
| UI-BUTTON-001 | Buttons | FOLLOW-UP | Not release blocking based on current evidence. |
| UI-STATUS-001 | Status Bar / Messages | PARTIALLY ADDRESSED | Data I/O result hints and OK output are visible. |
| UI-LINK-001 | Link Management | FUNCTIONALLY PASSED EARLIER | No new blocker in latest UAT. |
| UI-DELETE-001 | Deleted Data | ACCEPTED FOR CURRENT UAT | No new blocker in latest UAT. |
| UI-DATAIO-001 | Data I/O | UAT PASS | Guide, descriptions, result hint, OK result, and operations-log hint are visible. |
| UI-OPSLOG-001 | Operations Log | UAT PASS FOR GUIDANCE | Log guidance and controls are visible. Rich detail panel remains future scope. |
| UI-AUDIT-001 | Audit Logs | UAT PASS FOR DISPLAY | Pretty/diff-style display is visible. Export evidence remains optional unless required. |
| UI-USER-001 | User Management | FOLLOW-UP | Not in latest blocker set. |
| UI-HELP-001 | Help / Settings | FOLLOW-UP | Not in latest blocker set. |
| UI-DESIGN-SYSTEM-001 | UI Foundation | PARTIALLY ADDRESSED | Shared helpers are used in current slices. Full design system is future hardening. |
| UI-RESPONSIVE-001 | Layout | FOLLOW-UP | Not release blocking based on current evidence. |
| UI-COPY-001 | Copywriting | PARTIALLY ADDRESSED | Key Data I/O and subtitle microcopy improved. |
| UI-ACCESSIBILITY-001 | Accessibility | FOLLOW-UP | Not release blocking based on current evidence. |
| UI-KEYBOARD-001 | Keyboard Flow | FOLLOW-UP | Not release blocking based on current evidence. |
| UI-SEARCH-001 | Search UX | ACCEPTED FOR CURRENT UAT | Cross-parent subtitle search is future enhancement if requested. |
| UI-DETAIL-PANE-001 | Details | PARTIALLY ADDRESSED | Audit display and selected summaries improved. |
| UI-CONFIRM-001 | Confirmations | FOLLOW-UP | Not release blocking based on current evidence. |
| UI-MICROCOPY-001 | Guidance | PARTIALLY ADDRESSED | Data I/O, result, log, login, and subtitle guidance improved. |
| UI-ERROR-001 | Errors | FOLLOW-UP | Not release blocking based on current evidence. |
| UI-SUCCESS-001 | Success feedback | PARTIALLY ADDRESSED | Data I/O `[OK] CSV export 成功` is confirmed. |
| UI-RELEASE-POLISH-001 | Release Package | IN PROGRESS | docs/96 records final evidence. Final readiness decision remains. |

## 5. Current execution sequence status

| Sprint | Scope | Status |
|---|---|---|
| UI-0 | Restore green Quality Gates | DONE |
| UI-1 | Subtitle Management P0/P1 | DONE / UAT PASS |
| UI-2 | Common table and ID readability | PARTIAL / ACCEPTED FOR CURRENT UAT |
| UI-3 | Title Management + Link Management | ACCEPTED FOR CURRENT UAT / FOLLOW-UP |
| UI-4 | Login + role/status polish | DONE / UAT PASS |
| UI-5 | Data I/O + Logs/Audit | DONE / UAT PASS for observed scope |
| UI-6 | Help/Settings + P3 polish | FOLLOW-UP, not release-blocking under current evidence decision |
| UI-7 | Final UAT/docs/release | IN PROGRESS |

## 6. Immediate next actions

1. Synchronize `docs/94_ui_current_blockers_20260528.md` with the latest PASS evidence.
2. Make a release readiness decision.
3. If release-ready, keep P2/P3 items as follow-up backlog rather than release blockers.
4. If not release-ready, create explicit defect IDs for any remaining blockers.

## 7. Release readiness rule

Release can be marked `READY` if all of the following remain true:

- Latest Quality Gates are green.
- Current UAT evidence in `docs/96_final_uat_evidence_20260530.md` remains PASS for the release-critical observed scope.
- Audit export evidence remains optional or is explicitly waived.
- P2/P3 polish items are accepted as follow-up, not blockers.
- Any future cross-parent subtitle search/edit requirement is recorded as enhancement, not as a current release defect.

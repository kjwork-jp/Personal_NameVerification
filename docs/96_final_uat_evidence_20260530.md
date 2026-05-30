# 96_final_uat_evidence_20260530.md

## 1. Purpose

This document records the current final-UAT evidence based on the screenshot bundles provided by the user:

- `スクリーンショット 2026-05-30 070948.zip`
- `スクリーンショット 2026-05-30 085030.zip`

This document records the evidence observed from screenshots. It does not invent results for evidence that was not visible.

## 2. Code baseline

| Item | Value |
|---|---|
| Repository | `kjwork-jp/Personal_NameVerification` |
| Local pull evidence | User confirmed `git pull --ff-only` completed and updated `main` to `71a85fc008cd5746fb856db224efa9329c4d399a`. |
| Latest confirmed code Quality Gates | `138c15321845f56a756124e1fc9978446e23a5fb` / `chatgpt/quality-gates` success / run `26660843878`. |
| Workplan document | `docs/95_next_phase_workplan_20260530.md` |
| Evidence bundles | `スクリーンショット 2026-05-30 070948.zip`, `スクリーンショット 2026-05-30 085030.zip` |

## 3. Evidence summary

| Area | Judgment | Notes |
|---|---|---|
| Data I/O visual guidance | PASS | Guide tab, operation group descriptions, result hint, and Operations Log hint are visible in the submitted screenshots. |
| Data I/O action result | PASS | Export execution result shows `[OK] CSV export 成功`. |
| Subtitle list / parent display | PASS | Submitted screenshots show subtitle-specific columns and parent-title information split into title name, public ID, and state. |
| Subtitle selected-target flow | PASS | Edit and delete screenshots show concrete selected subtitle targets. |
| Subtitle row count | PASS / SPEC NOTE | Edit/delete show four subtitle rows for the selected parent title `sample-title-0000017`. This is treated as correct if the screen is scoped to the selected parent title. Cross-parent search/listing is a separate enhancement, not a release blocker for this UAT. |
| Login UI | PASS | Submitted screenshots show Windows/local authentication sections and the logged-in role context in the main window. |
| Audit UI | PASS | Submitted screenshots show readable change summary, before JSON, and after JSON sections. |
| Release readiness | PENDING DOC SYNC | UAT evidence is now PASS for the observed scope. Release decision still requires docs/status synchronization. |

## 4. Detailed UAT results

### 4.1 Data I/O

| Evidence ID | Judgment | Expected result | Observed result | Follow-up |
|---|---|---|---|---|
| EV-DATAIO-01 | PASS | Data I/O Guide tab shows page header and role guide. | Header and admin role guide are visible. | None. |
| EV-DATAIO-02 | PASS | Export / Backup / Restore / Import tabs show operation descriptions and existing controls. | Each operation tab shows guidance text and existing controls. | None. |
| EV-DATAIO-03 | PASS | Result area hint appears and `[OK]` / `[ERROR]` output semantics remain unchanged after operation. | Export result shows `[OK] CSV export 成功`. | None. |
| EV-DATAIO-04 | PASS | Operations Log tab shows guidance while filters, paging, search, and export remain available. | Guidance, filter/paging/search/export controls are visible. | None. |

### 4.2 Subtitle management

| Evidence ID | Judgment | Expected result | Observed result | Follow-up |
|---|---|---|---|---|
| EV-SUBTITLE-01 | PASS | Subtitle list shows subtitle rows, not title rows. | List columns include public ID, parent title, management number, subtitle name, state, display order, updated_at, and note. | None. |
| EV-SUBTITLE-02 | PASS | Parent title is split into title name, public ID, and state. | Add/edit/delete tabs show parent-title fields split into readable lines. | None. |
| EV-SUBTITLE-03 | PASS | Add/edit/delete target is clear before action. | Edit shows selected subtitle `sample-subtitle-0000065`; delete shows target subtitle `sample-subtitle-0000067`. | None. |
| EV-SUBTITLE-04 | PASS / SPEC NOTE | Edit/delete candidate list should show the subtitles under the selected parent title. | For selected parent `sample-title-0000017`, four subtitles are shown: `sample-subtitle-0000065` to `sample-subtitle-0000068`. | None for parent-scoped behavior. If cross-parent editing is later required, create a separate enhancement. |

### 4.3 Login

| Evidence ID | Judgment | Expected result | Observed result | Follow-up |
|---|---|---|---|---|
| EV-LOGIN-01 | PASS | Windows and local login sections are visible. | Login screen shows Windows authentication and local authentication sections. | None. |
| EV-LOGIN-02 | PASS | Role context appears after login. | Main window shows `ログイン中: admin / 権限: admin` in role/status areas. | None. |

### 4.4 Audit

| Evidence ID | Judgment | Expected result | Observed result | Follow-up |
|---|---|---|---|---|
| EV-AUDIT-01 | PASS | Pretty JSON and diff views are readable. | Submitted screenshots show readable change summary, before content, and after content sections. | None. |
| EV-AUDIT-02 | PARTIAL | Raw JSON fields are preserved in export. | Audit display is confirmed. Explicit audit export output evidence was not visible. | Optional follow-up only if audit export is required for release evidence. |

## 5. Remaining evidence needed

| ID | Priority | Difficulty | Required local evidence | Status |
|---|---:|---:|---|---|
| UAT-DATAIO-ACTION-RESULT | P0 | 3 | Run Export or Backup once and capture result area containing `[OK]`. | DONE |
| UAT-SUBTITLE-SELECTION | P0 | 3 | Select one subtitle in edit/delete flow and capture the selected-target summary. | DONE |
| UAT-AUDIT-001 | P1 | 3 | Capture audit pretty JSON/diff screen and, if possible, raw export evidence. | DISPLAY DONE / EXPORT OPTIONAL |

## 6. Current release decision

| Decision item | Result |
|---|---|
| Latest Quality Gates green | YES |
| Data I/O UAT complete | YES |
| Subtitle UAT complete | YES |
| Login UAT complete | YES |
| Audit display UAT complete | YES |
| Audit export evidence | OPTIONAL / PARTIAL |
| Docs synchronized | PARTIAL |
| Release readiness | PENDING DOC SYNC |

## 7. Next action

Synchronize `docs/91` and `docs/94` with the current UAT result, then make the final release readiness decision.

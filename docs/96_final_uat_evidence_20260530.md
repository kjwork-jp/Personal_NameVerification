# 96_final_uat_evidence_20260530.md

## 1. Purpose

This document records the current final-UAT evidence draft based on the screenshot bundle provided by the user:

- `スクリーンショット 2026-05-30 070948.zip`

This is not a full release approval yet. Items without direct screenshot or operation evidence remain `PARTIAL` or `NOT RUN`.

## 2. Code baseline

| Item | Value |
|---|---|
| Repository | `kjwork-jp/Personal_NameVerification` |
| Local pull evidence | User confirmed `git pull --ff-only` completed and updated `main` to `71a85fc008cd5746fb856db224efa9329c4d399a`. |
| Latest confirmed code Quality Gates | `138c15321845f56a756124e1fc9978446e23a5fb` / `chatgpt/quality-gates` success / run `26660843878`. |
| Workplan document | `docs/95_next_phase_workplan_20260530.md` |
| Evidence bundle | `スクリーンショット 2026-05-30 070948.zip` |

## 3. Evidence summary

| Area | Judgment | Notes |
|---|---|---|
| Data I/O visual guidance | PASS | Guide tab, operation group descriptions, result hint, and Operations Log hint are visible in the submitted screenshots. |
| Data I/O action result | PARTIAL | Result hint is visible, but a screenshot after executing Export or Backup with `[OK]` output is still required. |
| Subtitle list / parent display | PASS | Submitted screenshots show subtitle-specific columns and parent-title information split into title name, public ID, and state. |
| Subtitle selected-target flow | PARTIAL | Add flow context is visible. Edit/delete selected-target evidence is not complete because screenshots show `選択中サブタイトル 未選択`. |
| Login UI | PASS | Submitted screenshots show Windows/local authentication sections and the logged-in role context in the main window. |
| Audit UI | NOT RUN | No audit pretty-JSON/diff/export screenshot was included in the current evidence bundle. |
| Release readiness | BLOCKED | Remaining partial/not-run UAT items must be closed before release-ready judgment. |

## 4. Detailed UAT results

### 4.1 Data I/O

| Evidence ID | Judgment | Expected result | Observed result | Follow-up |
|---|---|---|---|---|
| EV-DATAIO-01 | PASS | Data I/O Guide tab shows page header and role guide. | Header and admin role guide are visible. | None. |
| EV-DATAIO-02 | PASS | Export / Backup / Restore / Import tabs show operation descriptions and existing controls. | Each operation tab shows guidance text and existing controls. | None. |
| EV-DATAIO-03 | PARTIAL | Result area hint appears and `[OK]` / `[ERROR]` output semantics remain unchanged after operation. | Result hint is visible. Operation execution result is not shown in current screenshots. | Capture Export or Backup result after one execution. |
| EV-DATAIO-04 | PASS | Operations Log tab shows guidance while filters, paging, search, and export remain available. | Guidance, filter/paging/search/export controls are visible. | None. |

### 4.2 Subtitle management

| Evidence ID | Judgment | Expected result | Observed result | Follow-up |
|---|---|---|---|---|
| EV-SUBTITLE-01 | PASS | Subtitle list shows subtitle rows, not title rows. | List columns include public ID, parent title, management number, subtitle name, state, display order, updated_at, and note. | None. |
| EV-SUBTITLE-02 | PASS | Parent title is split into title name, public ID, and state. | Add/edit/delete tabs show parent-title fields split into readable lines. | None. |
| EV-SUBTITLE-03 | PARTIAL | Add/edit/delete target is clear before action. | Add context is clear. Edit/delete screenshots still show no selected subtitle. | Capture edit/delete after selecting one subtitle row. |

### 4.3 Login

| Evidence ID | Judgment | Expected result | Observed result | Follow-up |
|---|---|---|---|---|
| EV-LOGIN-01 | PASS | Windows and local login sections are visible. | Login screen shows Windows authentication and local authentication sections. | None. |
| EV-LOGIN-02 | PASS | Role context appears after login. | Main window shows `ログイン中: admin / 権限: admin` in role/status areas. | None. |

### 4.4 Audit

| Evidence ID | Judgment | Expected result | Observed result | Follow-up |
|---|---|---|---|---|
| EV-AUDIT-01 | NOT RUN | Pretty JSON and diff views are readable. | No audit detail screenshot in current bundle. | Capture audit detail screen. |
| EV-AUDIT-02 | NOT RUN | Raw JSON fields are preserved in export. | No audit export evidence in current bundle. | Export audit data or capture export result. |

## 5. Remaining evidence needed

| ID | Priority | Difficulty | Required local evidence |
|---|---:|---:|---|
| UAT-DATAIO-ACTION-RESULT | P0 | 3 | Run Export or Backup once and capture result area containing `[OK]`. |
| UAT-SUBTITLE-SELECTION | P0 | 3 | Select one subtitle in edit/delete flow and capture the selected-target summary. |
| UAT-AUDIT-001 | P1 | 3 | Capture audit pretty JSON/diff screen and, if possible, raw export evidence. |

## 6. Current release decision

| Decision item | Result |
|---|---|
| Latest Quality Gates green | YES |
| Data I/O UAT complete | PARTIAL |
| Subtitle UAT complete | PARTIAL |
| Login UAT complete | YES |
| Audit UAT complete | NO |
| Docs synchronized | PARTIAL |
| Release readiness | BLOCKED |

## 7. Next action

Collect the three remaining local evidence items, then update this document from `PARTIAL / NOT RUN` to `PASS` or record explicit defects.

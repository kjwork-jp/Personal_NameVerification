# 91_editor_reuat_checksheet_20260528.md

## 1. Purpose

This document is the execution checksheet for the editor-role re-UAT after the 2026-05-27 editor follow-up fixes.

It should be used together with:

- `docs/72_v0_2_0_auth_integrated_uat_execution_record.md`
- `docs/75_v0_2_0_current_status_and_improvement_ledger.md`
- `docs/88_v040_uat_evidence_20260527.md`
- `docs/89_account_switch_viewer_uat_20260527.md`
- `docs/90_editor_uat_followup_20260527.md`
- `docs/97_open_issues_and_constraints.md`

## 2. Current baseline

| Item | Value |
|---|---|
| Target branch | `main` |
| Latest code-quality PASS commit | `6d9550f75dd1ecec32f9b7d9a2a084d8e76f6e48` |
| Latest Quality Gates run | `26549117150` |
| Quality Gates result | PASS: pytest, ruff, black, mypy |
| Release readiness before this re-UAT | BLOCKED |
| Blocker reason | editor GUI re-UAT is not yet completed |

## 3. Re-UAT scope

| Check ID | Finding ID | Area | Expected result | Status | Evidence |
|---|---|---|---|---|---|
| EDITOR-REUAT-001 | BUG-SUBTITLE-001 | Subtitle add | editor can create a subtitle. | NOT RUN | TBD |
| EDITOR-REUAT-002 | BUG-SUBTITLE-001 | Subtitle edit | editor can update an existing subtitle. | NOT RUN | TBD |
| EDITOR-REUAT-003 | UX-SUBTITLE-002 | Parent-title search | editor can search parent title by title word in subtitle add/edit. | NOT RUN | TBD |
| EDITOR-REUAT-004 | BUG-LINK-001 | Link unlink | editor can unlink an existing name-subtitle relation. | NOT RUN | TBD |
| EDITOR-REUAT-005 | BUG-EDITOR-001 | Title edit layout | title edit guidance and controls remain readable. | NOT RUN | TBD |
| EDITOR-REUAT-006 | BUG-EDITOR-001 | Subtitle add/edit layout | subtitle guidance and controls remain readable. | NOT RUN | TBD |
| EDITOR-REUAT-007 | Regression | Editor restricted operations | editor still cannot restore, hard-delete, Restore, or Import. | NOT RUN | TBD |
| EDITOR-REUAT-008 | Regression | Export / Backup | editor can still use Export and Backup according to policy. | NOT RUN | TBD |

## 4. Execution procedure

### 4.1 Prepare repository

```powershell
cd "C:\Users\nkaji\Documents\GitHub\Personal_NameVerification"
git checkout main
git pull
```

### 4.2 Optional local quality check

Quality Gates already passed on GitHub. Run this only when local confirmation is needed.

```powershell
python -m pytest -q
ruff check .
black --check .
mypy app
```

### 4.3 Launch UAT app

Use the existing demo reset/launch flow when a clean UAT state is required.

```powershell
.\scripts\reset_uat_demo_windows.ps1 -Launch
```

If a clean reset is not desired, launch the app normally.

```powershell
python -m app.pyside6_main
```

## 5. Detailed checks

### EDITOR-REUAT-001: Subtitle add

| Step | Action | Expected result | Actual result |
|---:|---|---|---|
| 1 | Login as editor. | MainWindow opens as editor. | TBD |
| 2 | Open `サブタイトル管理`. | Subtitle-focused screen is shown. | TBD |
| 3 | Open add/new workflow. | Parent title selector and subtitle fields are visible. | TBD |
| 4 | Select or search a parent title. | Create button becomes available. | TBD |
| 5 | Enter subtitle code/name and register. | Subtitle is created without error. | TBD |

### EDITOR-REUAT-002: Subtitle edit

| Step | Action | Expected result | Actual result |
|---:|---|---|---|
| 1 | Select a parent title. | Existing subtitles are listed. | TBD |
| 2 | Select an existing subtitle. | Subtitle fields are populated. | TBD |
| 3 | Update subtitle code/name/note. | Update button is available. | TBD |
| 4 | Execute update. | Subtitle is updated without error. | TBD |

### EDITOR-REUAT-003: Parent-title search

| Step | Action | Expected result | Actual result |
|---:|---|---|---|
| 1 | Open subtitle add/edit parent-title selector. | Selector is editable/searchable. | TBD |
| 2 | Type part of a title name. | Matching title candidates are suggested. | TBD |
| 3 | Select a candidate. | Selected parent title is reflected in the form. | TBD |

### EDITOR-REUAT-004: Link unlink

| Step | Action | Expected result | Actual result |
|---:|---|---|---|
| 1 | Open `関連付け`. | Register/unlink workflows are visible for editor. | TBD |
| 2 | Create or select an existing relation. | Existing relation is visible in unlink workflow. | TBD |
| 3 | Execute unlink. | Relation is removed/logically unlinked without permission error. | TBD |

### EDITOR-REUAT-005/006: Layout confirmation

| Step | Action | Expected result | Actual result |
|---:|---|---|---|
| 1 | Open title edit screen. | Guidance labels wrap and controls remain visible. | TBD |
| 2 | Open subtitle add screen. | Parent-title selector and subtitle fields are readable. | TBD |
| 3 | Open subtitle edit screen. | Guidance labels and edit controls are readable. | TBD |

### EDITOR-REUAT-007/008: Regression checks

| Step | Action | Expected result | Actual result |
|---:|---|---|---|
| 1 | Open deleted-data screen as editor. | Restore/hard-delete controls are hidden or unavailable. | TBD |
| 2 | Open Data I/O Restore/Import as editor. | Restore/Import are hidden or unavailable. | TBD |
| 3 | Open Data I/O Export/Backup as editor. | Export/Backup remain available. | TBD |

## 6. Judgment template

| Area | Judgment | Note |
|---|---|---|
| Subtitle add | TBD |  |
| Subtitle edit | TBD |  |
| Parent-title search | TBD |  |
| Link unlink | TBD |  |
| Layout | TBD |  |
| Restricted operations regression | TBD |  |
| Export / Backup regression | TBD |  |
| Overall editor re-UAT | TBD | PASS only if all P1 checks pass. |

## 7. Evidence naming policy

Recommended screenshot bundle name:

```text
スクリーンショット 2026-05-28 editor-reuat.zip
```

Recommended follow-up evidence update:

- Update `docs/90_editor_uat_followup_20260527.md` with the final re-UAT judgment.
- If all checks pass, update `docs/72`, `docs/75`, and `docs/97` from `BLOCKED` to the next release-readiness state.

## 8. Current status

| Item | Status |
|---|---|
| Fixes merged to main | DONE |
| Quality Gates | PASS |
| Checksheet prepared | DONE |
| Editor GUI re-UAT | NOT RUN |
| Release final Go/No-Go | BLOCKED |

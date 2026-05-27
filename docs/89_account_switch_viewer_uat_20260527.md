# 89_account_switch_viewer_uat_20260527.md

## 1. Purpose

This document records the follow-up UAT evidence for the account-switch database lifecycle fix and the viewer-role screen confirmation performed on 2026-05-27.

It supplements:

- `docs/72_v0_2_0_auth_integrated_uat_execution_record.md`
- `docs/88_v040_uat_evidence_20260527.md`
- `docs/97_open_issues_and_constraints.md`

## 2. Source evidence

| Source | Evidence |
|---|---|
| Console log | `git pull` confirmed the local repository was up to date after the account-switch fix and follow-up documentation updates. |
| Quality Gates / GitHub Actions | The latest `Quality Gates` runs on `main` / `push` passed after the earlier `DELETE-UX-001` failures were fixed by follow-up commits. |
| Prior failure log | Account switch to viewer previously raised `sqlite3.ProgrammingError: Cannot operate on a closed database`. |
| Fix commit | `a39c9f2dd4a81429c5d7c733a525279fd5a2f16c` / `fix: avoid closing shared database on account switch`. |
| Screenshot bundle | `スクリーンショット 2026-05-27 173946.zip` captured viewer-role screens after the account-switch fix. |
| User confirmation | User confirmed that the login/account-switch problem was resolved. |
| Viewer UI correction | User confirmed that viewer does not show restore, hard delete, Restore, Import, or other execution buttons in the captured screens. |

## 3. Root cause summary

`pyside6_main.py` keeps a shared SQLite connection and service graph across the account-switch loop.

Before the fix, the shared connection was passed into `MainWindow`. During account switch, `MainWindow.closeEvent()` closed that connection. The next `LoginDialog` then reused `UserService` backed by the closed connection, causing the following error during authentication:

```text
sqlite3.ProgrammingError: Cannot operate on a closed database
```

The fix avoids giving `MainWindow` ownership of the shared connection. The connection lifecycle remains owned by `pyside6_main.main()` and is closed only when the application exits.

## 4. Account switch UAT result

| UAT ID | Scenario | Expected result | Actual result | Judgment |
|---|---|---|---|---|
| ACC-SWITCH-DB-001 | Admin session switches to viewer login | Login dialog can authenticate viewer without closed DB error | User confirmed the login issue is resolved | PASS |
| ACC-SWITCH-DB-002 | Account switch after DB lifecycle fix | No `sqlite3.ProgrammingError` is emitted | No recurrence reported after fix | PASS |
| ACC-SWITCH-DB-003 | Viewer screen can be reached after account switch | Viewer-role screen is displayed after login | Viewer-role screenshots were captured after the fix | PASS |

## 5. Viewer screenshot evidence mapping

| Screenshot timestamp | Area | UAT / task mapping | Observed result | Judgment |
|---|---|---|---|---|
| `173925` | Deleted data / All | UAT-02, DELETE-UX-001-UAT | Viewer banner is visible. Hard-delete warning and danger styling are visible. Restore / hard-delete execution buttons are not shown for viewer. | PASS |
| `173926` | Deleted data / Names | UAT-02 | Viewer can view deleted names list. Restore / hard-delete execution buttons are not shown. | PASS |
| `173929` | Deleted data / Titles | UAT-02 | Viewer can view deleted titles list. Restore / hard-delete execution buttons are not shown. | PASS |
| `173931` | Deleted data / Subtitles | UAT-02 | Viewer can view deleted subtitles list. Restore / hard-delete execution buttons are not shown. | PASS |
| `173932` | Deleted data / Links | UAT-02 | Viewer can view deleted links list. Restore / hard-delete execution buttons are not shown. | PASS |
| `173935` | Data I/O / Operations Log | UAT-02, UAT-06-003 | Viewer can view Operations Log page. Execution buttons are not shown. | PASS |
| `173938` | Data I/O / Export | UAT-02, UAT-05 | Viewer sees the Export screen context, but export execution buttons are not shown in the captured viewer screen. | PASS |
| `173940` | Data I/O / Backup | UAT-02, UAT-05 | Viewer sees the Backup screen context, but backup execution buttons are not shown in the captured viewer screen. | PASS |
| `173942` | Data I/O / Restore | UAT-02, UAT-05 | Viewer sees the destructive Restore warning area. Restore execution buttons are not shown for viewer. | PASS |
| `173944` | Data I/O / Import | UAT-02, UAT-05 | Viewer sees the Import screen context and warning area. Import execution buttons are not shown for viewer. | PASS |
| `173946` | Data I/O / Operations Log / lower page | UAT-06-003 | Operations Log viewer context remains visible. Execution buttons are not shown. | PASS |
| `173948` | Data I/O / Restore or Import destructive area | UAT-02, UAT-05 | Red destructive warning area is visible in viewer context. Destructive execution buttons are not shown. | PASS |

## 6. Viewer operation-blocking judgment

The screenshot bundle confirms the following viewer-role behavior:

| Control area | Expected viewer behavior | Actual result | Judgment |
|---|---|---|---|
| Deleted data restore | Viewer must not restore deleted rows | Restore button is not shown | PASS |
| Deleted data hard delete | Viewer must not permanently delete rows | Hard-delete button is not shown | PASS |
| Data I/O Restore | Viewer must not execute restore | Restore execution button is not shown | PASS |
| Data I/O Import | Viewer must not execute import | Import execution button is not shown | PASS |
| Data I/O Export / Backup | Viewer must not execute restricted output operations if policy requires non-viewer role | Execution buttons are not shown in captured viewer screens | PASS |
| Normal mutation operations | Viewer must not create, update, or delete data | Execution buttons are not shown in captured viewer screens | PASS |

The viewer-role restriction is therefore established by UI-level hiding of execution controls in the captured screens, not by a visible-button runtime rejection flow.

## 7. Corrected interpretation

Previous evidence wording treated the viewer controls as if operation buttons were visible and needed click-based rejection confirmation. That interpretation was incorrect.

Correct interpretation:

- Viewer can navigate to read-only screens.
- Viewer can view deleted-data lists and operations-log views.
- Viewer does not see restore or hard-delete execution buttons.
- Viewer does not see Restore or Import execution buttons.
- Viewer does not see other mutation/execution buttons in the captured screens.
- Therefore, the captured viewer UAT evidence supports operation blocking by hidden buttons.

## 8. Remaining checks

The captured viewer screenshots are sufficient for the viewer hidden-button evidence in the observed screens. Remaining release work is outside this viewer correction.

| Remaining check | Status | Required evidence |
|---|---|---|
| Editor role UAT | REMAINING | Confirm editor can perform allowed normal operations and cannot perform admin-only destructive operations. |
| Admin final destructive-operation UAT | REMAINING if needed | Confirm admin-only destructive controls remain visible and executable after the viewer hidden-button confirmation. |
| Manual/docs consistency review | REMAINING | Compare README, operation manuals, `docs/72`, `docs/75`, `docs/88`, `docs/89`, and `docs/97` after final UAT state is fixed. |
| Release readiness judgment | REMAINING | Confirm no open UAT blockers remain before release preparation. |

## 9. Current judgment

| Area | Judgment |
|---|---|
| Account switch DB lifecycle fix | PASS |
| Viewer login after account switch | PASS |
| Viewer read-only navigation evidence | PASS |
| Viewer operation blocking by hidden execution buttons | PASS |
| Deleted-data danger warning visibility in viewer context | PASS |
| Viewer Restore / Import restriction | PASS |
| Viewer restore / hard-delete restriction | PASS |
| Editor role-specific evidence | REMAINING |
| Manual/docs final synchronization | REMAINING |
| Release readiness | Not final until editor evidence and docs sync are completed. |

## 10. Recommended next action

Proceed to UAT-03 editor verification.

Recommended editor checks:

| UAT ID | Scenario | Expected result |
|---|---|---|
| UAT-03-001 | Editor login after account switch | Editor can log in without DB lifecycle errors. |
| UAT-03-002 | Editor normal data registration/update | Editor can perform allowed create/update operations. |
| UAT-03-003 | Editor deleted-data restore / hard delete | Editor cannot restore or hard-delete deleted rows if those operations are admin-only. |
| UAT-03-004 | Editor Import / Restore | Editor cannot run destructive Import / Restore if those operations are admin-only. |
| UAT-03-005 | Editor Export / Backup | Editor behavior matches the defined role policy for Export / Backup. |

After UAT-03, synchronize the final evidence documents:

- `docs/72_v0_2_0_auth_integrated_uat_execution_record.md`
- `docs/75_v0_2_0_current_status_and_improvement_ledger.md`
- `docs/88_v040_uat_evidence_20260527.md`
- `docs/89_account_switch_viewer_uat_20260527.md`
- `docs/97_open_issues_and_constraints.md`

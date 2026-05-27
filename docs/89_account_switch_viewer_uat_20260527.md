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
| Console log | `git pull` updated `main` to `348ed5e`; `fix: wrap trash danger hint text` Quality Gates passed. |
| Prior failure log | Account switch to viewer previously raised `sqlite3.ProgrammingError: Cannot operate on a closed database`. |
| Fix commit | `a39c9f2dd4a81429c5d7c733a525279fd5a2f16c` / `fix: avoid closing shared database on account switch`. |
| Screenshot bundle | `スクリーンショット 2026-05-27 173946.zip` captured viewer-role screens after the account-switch fix. |
| User confirmation | User confirmed that the login/account-switch problem was resolved. |

## 3. Root cause summary

`pyside6_main.py` keeps a shared SQLite connection and service graph across the account-switch loop. The prior window construction passed that shared connection into `MainWindow`; `MainWindow.closeEvent()` then closed the connection during account switch. The next `LoginDialog` reused `UserService` backed by the closed connection, causing `Cannot operate on a closed database` during authentication.

The fix avoids giving `MainWindow` ownership of the shared connection. The connection lifecycle remains owned by `pyside6_main.main()` and is closed only when the application exits.

## 4. Account switch UAT result

| UAT ID | Scenario | Expected result | Actual result | Judgment |
|---|---|---|---|---|
| ACC-SWITCH-DB-001 | Admin session switches to viewer login | Login dialog can authenticate viewer without closed DB error | User confirmed the login issue is resolved | PASS |
| ACC-SWITCH-DB-002 | Account switch after DB lifecycle fix | No `sqlite3.ProgrammingError` is emitted | No recurrence reported after fix | PASS |

## 5. Viewer screenshot evidence mapping

| Screenshot timestamp | Area | UAT / task mapping | Observed result | Judgment |
|---|---|---|---|---|
| `173925` | Deleted data / All | UAT-02, DELETE-UX-001-UAT | Viewer banner is visible. Hard-delete warning and danger styling are visible. Restore / hard-delete buttons are present but viewer should remain blocked by role guards. | PASS with control note |
| `173926` | Deleted data / Names | UAT-02 | Viewer can view deleted names list. | PASS |
| `173929` | Deleted data / Titles | UAT-02 | Viewer can view deleted titles list. | PASS |
| `173931` | Deleted data / Subtitles | UAT-02 | Viewer can view deleted subtitles list. | PASS |
| `173932` | Deleted data / Links | UAT-02 | Viewer can view deleted links list. | PASS |
| `173935` | Data I/O / Operations Log | UAT-02, UAT-06-003 | Viewer can view Operations Log page. | PASS |
| `173938` | Data I/O / Export | UAT-02, UAT-05 | Viewer sees export screen and warning. Buttons/operation availability still require functional restriction confirmation. | PASS with control note |
| `173940` | Data I/O / Backup | UAT-02, UAT-05 | Viewer sees backup screen. Controls require role-guard confirmation. | PASS with control note |
| `173942` | Data I/O / Restore | UAT-02, UAT-05 | Viewer sees destructive restore warning area. Restore operation must remain blocked for viewer. | PASS with control note |
| `173944` | Data I/O / Import | UAT-02, UAT-05 | Viewer sees import screen and warning. Import operation must remain blocked for viewer. | PASS with control note |
| `173946` | Data I/O / Operations Log / lower page | UAT-06-003 | Operations Log viewer context remains visible. | PASS |
| `173948` | Data I/O / Restore or Import destructive area | UAT-02, UAT-05 | Red destructive warning area is visible in viewer context. | PASS with control note |

## 6. Remaining viewer-role control checks

The screenshot bundle confirms viewer login, role banner display, read-only screen reachability, and no recurrence of the closed database authentication failure. It does not, by itself, fully prove every blocked operation because disabled/enabled button state and rejected execution messages may require direct click testing.

| Remaining check | Status | Required evidence |
|---|---|---|
| Viewer cannot create/update/delete normal data | REMAINING | Attempt or UI disabled-state screenshot for name/title/subtitle/link mutation controls. |
| Viewer cannot restore or hard-delete trash rows | REMAINING | Attempt or disabled-state screenshot/message for restore and hard-delete. |
| Viewer cannot run import/restore destructive Data I/O | REMAINING | Attempt or disabled-state screenshot/message for import/restore execution. |
| Viewer export/backup policy | REMAINING | Confirm whether viewer should be allowed to export/backup, then capture evidence accordingly. |

## 7. Current judgment

| Area | Judgment |
|---|---|
| Account switch DB lifecycle fix | PASS |
| Viewer login after account switch | PASS |
| Viewer read-only navigation evidence | PARTIAL PASS |
| Viewer operation-blocking evidence | REMAINING |
| Release readiness | Not final until viewer/editor control evidence and docs sync are completed. |

## 8. Recommended next action

Continue UAT-02 as viewer. Capture evidence for blocked operations, especially restore/hard-delete and import/restore. Then proceed to UAT-03 editor restrictions.

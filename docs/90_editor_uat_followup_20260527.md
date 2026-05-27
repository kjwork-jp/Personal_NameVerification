# 90_editor_uat_followup_20260527.md

## 1. Purpose

This document records the 2026-05-27 editor-role UAT findings and the follow-up fixes applied after the viewer hidden-button UAT evidence was corrected in `docs/89_account_switch_viewer_uat_20260527.md`.

It supplements:

- `docs/72_v0_2_0_auth_integrated_uat_execution_record.md`
- `docs/75_v0_2_0_current_status_and_improvement_ledger.md`
- `docs/88_v040_uat_evidence_20260527.md`
- `docs/89_account_switch_viewer_uat_20260527.md`
- `docs/97_open_issues_and_constraints.md`

## 2. Source evidence

| Source | Evidence |
|---|---|
| Editor UAT report | User reported editor login and several allowed/blocked operations were OK, but found subtitle, link-unlink, search, and layout issues. |
| Prior viewer UAT | Viewer operation controls were confirmed hidden, not merely disabled. |
| Quality Gates before follow-up fixes | A prior run passed pytest but failed at ruff due to `B009`. |
| Latest retained fix commit | `ac2d182c8aae39b12b1721cddc968cf88196f7e5` / `test: replace constant getattr in editor UAT tests`. |

## 3. Editor UAT result summary

| UAT ID | Area | Result | Judgment |
|---|---|---|---|
| UAT-03-001 | Editor login | Editor login worked without the closed-database account-switch error. | PASS |
| UAT-03-002-A | Name add/edit | New name creation and edit worked. | PASS |
| UAT-03-002-B | Title add/edit | Title creation and edit worked functionally, but layout needed improvement. | PASS with UI finding |
| UAT-03-002-C | Subtitle add/edit | Subtitle add/edit was not possible in the observed UAT. | FAIL before fix |
| UAT-03-002-D | Link registration | Link registration worked. | PASS |
| UAT-03-002-E | Link unlink/removal | Link registration worked, but unlink/removal did not. | FAIL before fix |
| UAT-03-003 | Deleted-data restore/hard-delete as editor | Restore/hard-delete controls were hidden or unavailable. | PASS |
| UAT-03-004 | Data I/O Restore/Import as editor | Restore/Import were hidden or unavailable. | PASS |
| UAT-03-005 | Data I/O Export/Backup as editor | Export/Backup matched the editor policy and were available. | PASS |

## 4. Findings

| Finding ID | Priority | Type | Finding | Release impact |
|---|---:|---|---|---|
| BUG-EDITOR-001 | P1 | UI | UI layout was cramped/broken, especially title edit and explanatory-comment areas. | Release blocker until acceptable. |
| BUG-SUBTITLE-001 | P1 | Function | Subtitle add/edit was not possible. | Release blocker. |
| UX-SUBTITLE-002 | P2 | UX | Subtitle add screen did not support title word search. | Strong release candidate improvement. |
| BUG-LINK-001 | P1 | Function | Link registration worked, but unlink/removal did not. | Release blocker. |

## 5. Follow-up fixes applied

| Commit | Area | Summary |
|---|---|---|
| `9703e8d` | UI permission | Allowed editor unlink permission in UI helpers. |
| `5fdacd9` | Subtitle UI | Improved subtitle editor search and layout. |
| `0e1d8ea` | Title UI | Wrapped title-management guidance labels. |
| `892bed2` | Service authorization | Allowed editor relation unlink authorization for subtitle links. |
| `3060a82` | Tests | Added editor UAT follow-up regression tests. |
| `384704f` | Service tests | Added editor subtitle unlink service coverage. |
| `2d5dadf` | Link UI tests | Aligned editor unlink button expectation. |
| `cf22557` | RBAC UI tests | Aligned editor link RBAC expectation. |
| `b91aae8` | Release UAT tests | Aligned editor link UAT visibility. |
| `e5f5052` | Follow-up tests | Fixed editor UAT follow-up lint formatting, but a later ruff B009 remained. |
| `ac2d182c8aae39b12b1721cddc968cf88196f7e5` | Follow-up tests | Replaced constant-name `getattr()` calls with typed payload access. |

## 6. Current quality-gate status

| Item | Status | Note |
|---|---|---|
| Known previous failing run | FAIL | pytest passed; ruff failed with B009 before `ac2d182`. |
| Latest retained fix commit | CONFIRMED PUSHED | `ac2d182c8aae39b12b1721cddc968cf88196f7e5`. |
| Actions lookup from connector | LIMITED | Commit workflow-run lookup returned no push-run rows, so the final push-run result still requires `Quality Gates` run confirmation. |
| Release readiness | BLOCKED | Requires latest Quality Gates PASS plus editor re-UAT. |

## 7. Re-UAT checklist

| Check ID | Scenario | Expected result |
|---|---|---|
| BUG-SUBTITLE-001-UAT-ADD | Editor creates a subtitle | Subtitle creation works. |
| BUG-SUBTITLE-001-UAT-EDIT | Editor updates a subtitle | Subtitle update works. |
| UX-SUBTITLE-002-UAT | Editor searches parent title in subtitle add/edit | Title can be found by word search / contains matching. |
| BUG-LINK-001-UAT | Editor unlinks an existing relation | Existing relation can be unlinked by editor. |
| BUG-EDITOR-001-UAT | Title/subtitle guidance and edit layout | Explanatory labels wrap, and controls remain readable. |

## 8. Current judgment

| Area | Judgment |
|---|---|
| Editor login | PASS |
| Name add/edit | PASS |
| Title add/edit | PASS with UI follow-up applied |
| Subtitle add/edit | FIX APPLIED / RE-UAT REQUIRED |
| Subtitle title search | FIX APPLIED / RE-UAT REQUIRED |
| Link unlink/removal | FIX APPLIED / RE-UAT REQUIRED |
| UI layout | FIX APPLIED / RE-UAT REQUIRED |
| Latest Quality Gates | CONFIRMATION REQUIRED |
| Release readiness | Not final until Quality Gates and editor re-UAT pass. |

## 9. Recommended next action

1. Confirm the latest `Quality Gates` result for `ac2d182c8aae39b12b1721cddc968cf88196f7e5` or later.
2. If Quality Gates passes, rerun editor UAT for subtitle add/edit, title search, relation unlink, and layout.
3. If re-UAT passes, synchronize `docs/72`, `docs/75`, `docs/88`, `docs/89`, `docs/90`, and `docs/97`.
4. Keep release preparation blocked until these checks are complete.

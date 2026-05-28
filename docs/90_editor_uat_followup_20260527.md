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
| Quality Gates before follow-up fixes | Prior runs failed on old editor-unlink expectations and ruff formatting/lint issues. |
| Latest passing fix commit | `6d9550f75dd1ecec32f9b7d9a2a084d8e76f6e48` / `test: fix release UAT ruff issues`. |
| Latest passing run | `26549117150`; pytest, ruff, black, and mypy all passed. |

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
| `706034c6c47feb08b0b69f5b2e1c89c762bd960c` | Follow-up tests | Shortened editor UAT regression tests after additional ruff failure. |
| `6d9550f75dd1ecec32f9b7d9a2a084d8e76f6e48` | Release UAT tests | Fixed final release UAT ruff issues. |

## 6. Current quality-gate status

| Item | Status | Note |
|---|---|---|
| Known previous failing runs | RESOLVED | Prior failures were caused by old editor-unlink expectations and ruff issues. |
| Latest retained fix commit | PASS | `6d9550f75dd1ecec32f9b7d9a2a084d8e76f6e48`. |
| Latest Quality Gates run | PASS | Run `26549117150`. |
| pytest | PASS | Confirmed by Quality Gates job. |
| ruff | PASS | Confirmed by Quality Gates job. |
| black check | PASS | Confirmed by Quality Gates job. |
| mypy | PASS | Confirmed by Quality Gates job. |
| Release readiness | BLOCKED | Requires editor re-UAT evidence despite Quality Gates passing. |

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
| Latest Quality Gates | PASS |
| Release readiness | Not final until editor re-UAT passes. |

## 9. Recommended next action

1. Rerun editor UAT for subtitle add/edit, title search, relation unlink, and layout.
2. If re-UAT passes, synchronize `docs/72`, `docs/75`, `docs/88`, `docs/89`, `docs/90`, and `docs/97`.
3. Keep release preparation blocked until these checks are complete.

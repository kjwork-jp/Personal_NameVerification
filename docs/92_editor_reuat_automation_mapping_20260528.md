# 92_editor_reuat_automation_mapping_20260528.md

## 1. Purpose

This document maps the editor re-UAT checks in `docs/91_editor_reuat_checksheet_20260528.md` to automated evidence that already exists in the repository.

The goal is to reduce manual GUI confirmation to the minimum required visual checks.

Related documents:

- `docs/72_v0_2_0_auth_integrated_uat_execution_record.md`
- `docs/75_v0_2_0_current_status_and_improvement_ledger.md`
- `docs/90_editor_uat_followup_20260527.md`
- `docs/91_editor_reuat_checksheet_20260528.md`
- `docs/97_open_issues_and_constraints.md`

## 2. Current automated baseline

| Item | Value |
|---|---|
| Target branch | `main` |
| Latest full Quality Gates PASS commit | `6d9550f75dd1ecec32f9b7d9a2a084d8e76f6e48` |
| Latest full Quality Gates PASS run | `26549117150` |
| Gates included | pytest, ruff, black, mypy |
| Commit status context | `chatgpt/quality-gates` |
| Manual GUI re-UAT status | NOT RUN |

## 3. Re-UAT to automation mapping

| Re-UAT ID | Manual check | Automated coverage | Automation status | Manual still required? | Note |
|---|---|---|---|---|---|
| EDITOR-REUAT-001 | editor can create a subtitle | `tests/test_editor_uat_followup_ui.py::test_subtitle_editor_can_create_and_update_as_editor` | COVERED | YES, one GUI confirmation | Confirms service call and editor role propagation in UI-level test. |
| EDITOR-REUAT-002 | editor can update a subtitle | `tests/test_editor_uat_followup_ui.py::test_subtitle_editor_can_create_and_update_as_editor` | COVERED | YES, one GUI confirmation | Confirms update path and editor role propagation in UI-level test. |
| EDITOR-REUAT-003 | parent title can be searched by title word | `tests/test_editor_uat_followup_ui.py::test_subtitle_parent_title_selector_is_searchable` | COVERED | YES, visual/operability confirmation | Confirms editable combo, completer, and state refresh property. |
| EDITOR-REUAT-004 | editor can unlink an existing relation | `tests/test_editor_uat_followup_ui.py::test_editor_can_unlink_existing_relation`; `tests/test_core_services.py::test_editor_can_link_and_unlink_subtitle_relation` | COVERED | YES, one GUI confirmation | Covers both UI call path and service authorization. |
| EDITOR-REUAT-005 | title edit layout is readable | `tests/test_editor_uat_followup_ui.py::test_title_management_guidance_labels_are_wrapped` | PARTIAL | YES | Automated test confirms wrapping properties, but visual layout requires screenshot confirmation. |
| EDITOR-REUAT-006 | subtitle add/edit layout is readable | `tests/test_editor_uat_followup_ui.py::test_subtitle_parent_title_selector_is_searchable` | PARTIAL | YES | Automated test confirms selector/search state, but visual layout requires screenshot confirmation. |
| EDITOR-REUAT-007 | editor cannot run restricted operations | `tests/test_rbac_ui_guards.py`; `tests/test_release_uat_coverage.py` | COVERED | LOW | Manual spot-check recommended only because this is release-blocker-sensitive. |
| EDITOR-REUAT-008 | editor can use Export / Backup | `tests/test_rbac_ui_guards.py`; `tests/test_release_uat_coverage.py` | COVERED | LOW | Manual spot-check recommended only because this is release-blocker-sensitive. |

## 4. Minimal manual GUI evidence still required

Automated evidence is sufficient to reduce the manual GUI scope to the following screenshots or observations:

| Required evidence | Why still manual |
|---|---|
| Subtitle add screen after selecting/searching a parent title | Confirms actual visible usability, not only widget properties. |
| Subtitle edit screen after selecting a subtitle | Confirms field population and visible update path. |
| Link unlink screen showing editor can access unlink workflow | Confirms user-facing workflow availability. |
| Title edit screen showing guidance/layout readability | Visual layout cannot be fully judged by unit tests. |
| Data I/O / restricted operation spot-check as editor | Confirms no regression in role-gated navigation. |

## 5. Recommended evidence bundle

Recommended screenshot bundle name:

```text
スクリーンショット 2026-05-28 editor-reuat.zip
```

Recommended screenshots:

| Screenshot | Target |
|---|---|
| `editor_subtitle_add_search.png` | Subtitle add screen with parent title search text entered. |
| `editor_subtitle_add_success.png` | Subtitle add completed or created row visible. |
| `editor_subtitle_edit_success.png` | Subtitle edit completed or updated row visible. |
| `editor_link_unlink.png` | Existing relation selected in unlink workflow. |
| `editor_link_unlink_success.png` | Relation removed or success message visible. |
| `editor_title_edit_layout.png` | Title edit screen after guidance wrapping. |
| `editor_dataio_restricted.png` | Restore/Import hidden or unavailable for editor. |
| `editor_export_backup.png` | Export/Backup available for editor. |

## 6. Release judgment impact

| Condition | Release readiness impact |
|---|---|
| All EDITOR-REUAT-001〜008 pass | Release can move from BLOCKED to release Go/No-Go final review. |
| Any P1 check fails | Release remains BLOCKED; create follow-up fix and rerun Quality Gates. |
| Only minor visual issue remains | Conditional Go may be considered if no data loss, RBAC, auth, or migration risk remains. |

## 7. Current status

| Item | Status |
|---|---|
| Automated coverage mapping | DONE |
| Full Quality Gates | PASS at `6d9550f75dd1ecec32f9b7d9a2a084d8e76f6e48` |
| Manual editor re-UAT | NOT RUN |
| Release final Go/No-Go | BLOCKED |

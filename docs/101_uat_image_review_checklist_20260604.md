# 101_uat_image_review_checklist_20260604.md

## 1. Purpose

This document converts the 2026-06-04 UAT screenshot review findings into a reusable local UAT checklist.

Use this checklist when reviewing local GUI screenshots before release judgment. The scope is visual and workflow confirmation only. Do not commit generated DB, CSV, export, backup, or screenshot archive files.

## 2. Status legend

| Status | Meaning |
|---|---|
| NOT RUN | Not executed yet |
| PASS | Expected behavior confirmed |
| FAIL | Unexpected behavior found |
| N/A | Not applicable with reason |
| ACCEPTED | Known limitation accepted |

## 3. Evidence naming policy

Recommended screenshot bundle name:

```text
screenshots_YYYYMMDD_local_uat_image_review.zip
```

Recommended individual screenshot naming:

```text
YYYYMMDD_<role-or-area>_<check-id>_<short-description>.png
```

Examples:

- `20260604_viewer_IMG-UAT-001_navigation.png`
- `20260604_editor_IMG-UAT-002_hidden_admin_features.png`
- `20260604_admin_IMG-UAT-003_all_features.png`

## 4. UAT setup checklist

| ID | Status | Check | Evidence / Notes |
|---|---|---|---|
| SETUP-001 | NOT RUN | Start from the target branch and confirm it is up to date with the intended UAT baseline. |  |
| SETUP-002 | NOT RUN | Launch the application with the intended local UAT database. |  |
| SETUP-003 | NOT RUN | Prepare login accounts for Viewer, Editor, and Admin. |  |
| SETUP-004 | NOT RUN | Confirm browser/window size or desktop display scaling used for screenshots. |  |
| SETUP-005 | NOT RUN | Confirm generated screenshots and runtime data are not tracked by git. |  |

## 5. Checklist summary

| ID | Status | Area | Primary role | Evidence / Notes |
|---|---|---|---|---|
| IMG-UAT-001 | NOT RUN | Viewer visible features | Viewer |  |
| IMG-UAT-002 | NOT RUN | Editor hidden admin features | Editor |  |
| IMG-UAT-003 | NOT RUN | Admin visible features | Admin |  |
| IMG-UAT-004 | NOT RUN | Duplicate name/title/subtitle prevention | Editor or Admin |  |
| IMG-UAT-005 | NOT RUN | Title edit screen layout | Editor or Admin |  |
| IMG-UAT-006 | NOT RUN | Subtitle edit from subtitle-focused workflow | Editor or Admin |  |
| IMG-UAT-007 | NOT RUN | Minimal list columns | Viewer, Editor, Admin as needed |  |
| IMG-UAT-008 | NOT RUN | Full information in detail pane / selection card | Viewer, Editor, Admin as needed |  |
| IMG-UAT-009 | NOT RUN | Audit log diff readability | Admin |  |
| IMG-UAT-010 | NOT RUN | Datetime display format | Viewer, Editor, Admin as needed |  |

## 6. Detailed checklist

### IMG-UAT-001: Viewer shows only Search and Help

| Item | Content |
|---|---|
| Confirmation steps | 1. Login as Viewer. 2. Capture the main navigation immediately after login. 3. Open each visible navigation item. 4. Confirm no create, edit, delete, restore, import, export, audit, or user-management entry point is visible. |
| Expected result | Viewer can see and use only search-related screens and Help. Viewer cannot see management tabs, destructive workflows, audit logs, Data I/O, deleted data, or user management. |
| NG examples | Viewer navigation contains title management, subtitle management, related-link editing, deleted data, audit log, Data I/O, user management, import, restore, hard delete, or other admin/editor-only operations. Disabled admin buttons are still visible without a clear reason. |
| Screenshot evidence to capture | Main navigation after Viewer login. Search screen with result/details visible. Help screen visible from Viewer. Optional screenshot showing that admin/editor tabs are absent from the Viewer navigation area. |

### IMG-UAT-002: Editor does not show deleted data, audit log, Data I/O, or user management

| Item | Content |
|---|---|
| Confirmation steps | 1. Login as Editor. 2. Capture the full main navigation. 3. Review all top-level tabs, menus, and any settings/help shortcuts. 4. Confirm normal editing workflows remain available. 5. Confirm deleted data, audit log, Data I/O, and user management are not visible. |
| Expected result | Editor can access normal data editing workflows required for name/title/subtitle/link maintenance. Editor cannot see deleted data, audit log, Data I/O, or user management entry points. |
| NG examples | Editor sees `削除データ`, `監査ログ`, `データ入出力`, `ユーザー管理`, restore, import, hard delete, operations log, user role change, or equivalent admin-only controls. Editor sees admin-only tabs even if the buttons are disabled. |
| Screenshot evidence to capture | Editor main navigation. Editor normal edit screen showing allowed work remains available. Screenshot of the navigation/menu area where deleted data, audit log, Data I/O, and user management would appear for Admin, proving they are absent for Editor. |

### IMG-UAT-003: Admin shows all features

| Item | Content |
|---|---|
| Confirmation steps | 1. Login as Admin. 2. Capture the full main navigation. 3. Open each major feature area once. 4. Confirm search, name/title/subtitle/link management, deleted data, audit log, Data I/O, user management, and Help are all reachable. |
| Expected result | Admin can see all application features and all admin-only feature areas. Destructive areas are visually distinguishable from normal editing workflows. |
| NG examples | Admin cannot see deleted data, audit log, Data I/O, user management, import, restore, hard delete, or any normal editing workflow. Admin-only controls are hidden or unreachable. Destructive controls appear in a normal editing area without visual separation. |
| Screenshot evidence to capture | Admin main navigation. Deleted data screen. Audit log screen. Data I/O screen. User management screen. One normal editing screen confirming Admin can still use standard workflows. |

### IMG-UAT-004: Duplicate name/title/subtitle registration is detected and blocked

| Item | Content |
|---|---|
| Confirmation steps | 1. Login as Editor or Admin. 2. Prepare an existing name, title, and subtitle from the UAT database. 3. Attempt to register a duplicate name with the same identifying fields. 4. Attempt to register a duplicate title with the same identifying fields. 5. Attempt to register a duplicate subtitle under the same parent title with the same identifying fields. 6. Confirm each duplicate attempt is rejected before a new row is created. |
| Expected result | Duplicate registration for name, title, and subtitle is detected and prohibited. The user receives a clear error or warning that identifies the duplicate condition. No duplicate record is added to the list, detail pane, database, or audit history as a successful create. |
| NG examples | Duplicate name/title/subtitle is registered successfully. Duplicate detection only happens after the list already contains the new duplicate. The message is vague, missing, or points to the wrong entity. Duplicate subtitle is blocked globally when it should only be judged within the correct parent-title context, or allowed within the same parent when it should be blocked. |
| Screenshot evidence to capture | Existing record before duplicate attempt. Duplicate input form before submission. Error/warning message after submission. List or detail pane after rejection showing no duplicate was added. Repeat evidence for name, title, and subtitle. |

### IMG-UAT-005: Title edit screen has no UI collapse or layout breakage

| Item | Content |
|---|---|
| Confirmation steps | 1. Login as Editor or Admin. 2. Open title management. 3. Select an existing title. 4. Open the title edit view. 5. Review labels, input fields, guidance text, buttons, validation messages, and selection cards at the target screenshot size. 6. Resize or scroll only as expected for the application and confirm the layout remains readable. |
| Expected result | Title edit controls are aligned and readable. Text does not overlap. Buttons are visible and not clipped. Guidance text wraps cleanly. The selected title context remains clear. There is no excessive horizontal scrolling or compressed control group. |
| NG examples | Labels overlap inputs. Buttons are clipped or outside the visible area. Guidance text pushes controls out of view. The edit form is too narrow to read. Selected title context is missing. The title edit screen accidentally shows subtitle mutation controls that should belong to subtitle management. |
| Screenshot evidence to capture | Title list with selected title. Title edit screen before edit. Title edit screen with representative long values if available. Any validation message or save confirmation used during the layout check. |

### IMG-UAT-006: Subtitle edit can be started from the subtitle-focused workflow

| Item | Content |
|---|---|
| Confirmation steps | 1. Login as Editor or Admin. 2. Open subtitle management, not title management. 3. Search or select a subtitle from the subtitle-focused list or selector. 4. Open the subtitle edit view from that subtitle selection. 5. Edit a subtitle field and submit if the UAT run permits data mutation. |
| Expected result | Subtitle edit can be performed from a subtitle starting point. The user does not need to begin from a title edit screen to find and edit a subtitle. Parent title context is still visible enough to avoid editing the wrong subtitle. |
| NG examples | Subtitle can only be edited after first selecting a title. Subtitle management does not provide a direct subtitle selection/edit path. Parent title context is missing after selecting a subtitle. The edit screen is actually title-focused and mixes unrelated title mutation controls. |
| Screenshot evidence to capture | Subtitle management entry screen. Subtitle list/search result with target subtitle selected. Subtitle edit screen opened from the subtitle selection. Parent title context shown on the subtitle edit screen. Save confirmation or updated detail pane if mutation is performed. |

### IMG-UAT-007: List columns are limited to the minimum necessary fields

| Item | Content |
|---|---|
| Confirmation steps | 1. Open the main list views used during UAT, including search results and management lists. 2. Review the visible columns for names, titles, subtitles, links, deleted data, and audit logs where applicable. 3. Confirm each list is optimized for scanning and selection, not full detail inspection. 4. Confirm removed details are still available in the detail pane or selection card covered by IMG-UAT-008. |
| Expected result | Lists show only the fields needed to identify, compare, and select rows. Dense metadata, long notes, full descriptions, and secondary fields are not forced into the list when they belong in detail views. |
| NG examples | List contains too many columns to scan. Important identifiers are pushed off-screen. Long text columns dominate the table. Horizontal scrolling is required for normal row selection. The list removes necessary identity fields without providing them elsewhere. |
| Screenshot evidence to capture | Search result list. Name management list if present. Title management list. Subtitle management list. Link or related-item list. Deleted data and audit lists if applicable to the role under test. |

### IMG-UAT-008: Detail pane or selection card shows all information

| Item | Content |
|---|---|
| Confirmation steps | 1. Select representative rows from the minimal lists checked in IMG-UAT-007. 2. Inspect the detail pane or selection card for each selected name, title, subtitle, and link. 3. Confirm all fields removed from the list remain visible in the detail area. 4. Confirm long values and notes wrap or scroll in a readable way. |
| Expected result | The detail pane or selection card contains the full information needed to verify the selected record. The selected row and detail area are clearly connected. Long text remains readable without overlap or clipping. |
| NG examples | A field removed from the list is not available anywhere. Detail pane shows stale data after selecting another row. Selected row and detail card disagree. Long notes or metadata are clipped. The user must open an unrelated edit form just to inspect read-only details. |
| Screenshot evidence to capture | List with a selected row and corresponding detail pane visible. Name detail. Title detail. Subtitle detail. Link/detail relation view. Any long text or metadata example that proves wrapping or scrolling works. |

### IMG-UAT-009: Audit log diff is readable

| Item | Content |
|---|---|
| Confirmation steps | 1. Login as Admin. 2. Open audit log or data change log. 3. Select entries for create, update, and delete/restore if available. 4. Review before/after values and diff display. 5. Confirm sensitive values such as password hashes are not exposed. |
| Expected result | Audit log diff clearly separates before and after values. Changed fields are easy to identify. JSON or structured values are formatted readably enough for UAT review. Timestamps, actor, action, entity, and target are visible. Sensitive authentication values are masked or absent. |
| NG examples | Diff is a single unreadable blob. Before and after values are not distinguishable. Changed fields cannot be identified. Long JSON is clipped with no way to inspect it. Password, password hash, password salt, token, or equivalent sensitive values are visible. |
| Screenshot evidence to capture | Audit log list. Selected create entry with detail/diff. Selected update entry with before/after diff. Selected delete or restore entry if available. Example showing sensitive fields are absent or masked when the relevant event exists. |

### IMG-UAT-010: Datetime is displayed as YYYY/MM/DD HH:MM:SS

| Item | Content |
|---|---|
| Confirmation steps | 1. Review all screens that display dates or datetimes during UAT. 2. Include search results, detail panes, edit metadata, deleted data, audit logs, Data I/O operations log, backup/export history, and user management if visible for the role. 3. Confirm each datetime uses `YYYY/MM/DD HH:MM:SS`. 4. Confirm date-only values are intentionally date-only if any exist. |
| Expected result | Datetime values are consistently displayed in `YYYY/MM/DD HH:MM:SS` format, for example `2026/06/04 09:30:05`. The display does not mix hyphenated dates, ISO `T` separators, timezone suffixes, or missing seconds in datetime fields. |
| NG examples | Datetime appears as `2026-06-04 09:30:05`, `2026-06-04T09:30:05`, `2026/06/04 09:30`, `06/04/2026 09:30:05`, raw epoch values, or a mixture of multiple formats on the same screen. |
| Screenshot evidence to capture | At least one screen with ordinary record timestamps. Audit log timestamp. Deleted data timestamp if visible. Data I/O or operations log timestamp if visible. User management timestamp if visible. |

## 7. Findings register

| Finding ID | Severity | Related check | Summary | Decision | Follow-up |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## 8. UAT exit decision

| Item | Status | Notes |
|---|---|---|
| All checks complete | NOT RUN |  |
| All role visibility screenshots captured | NOT RUN | Viewer, Editor, and Admin evidence are required. |
| Duplicate prevention confirmed | NOT RUN | Name, title, and subtitle are all required. |
| Layout and workflow checks passed | NOT RUN | Title edit and subtitle-focused edit are required. |
| List/detail information split confirmed | NOT RUN | Minimal list plus full detail evidence are required. |
| Audit and datetime display confirmed | NOT RUN | Admin-only evidence is acceptable for admin-only screens. |
| No blocker remains | NOT RUN |  |
| Release judgment can proceed | NOT RUN | Only after all required evidence is reviewed. |

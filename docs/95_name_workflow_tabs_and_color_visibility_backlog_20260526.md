# 95_name_workflow_tabs_and_color_visibility_backlog_20260526.md

## Purpose

This document tracks the UI feedback that the name management tab should follow the same workflow separation pattern as title/subtitle management, and that the application needs stronger visual differentiation through semantic colors.

## UAT feedback

| Item | Value |
|---|---|
| Finding ID | UAT-F-004 |
| Severity | fix before release |
| Area | Name management UI / visual design |
| Summary | Name management should also separate list, add, edit, delete, and guide workflows. Color usage should be expanded to improve visibility. |
| Release impact | Release preparation should remain deferred until workflow separation and visibility checks pass. |

## Implemented changes

| ID | Priority | Area | Status | Candidate |
|---|---:|---|---|---|
| V040-UX-003 | P2 | UI | Implemented / Actions pending / UAT re-check pending | Split name management into workflow tabs |
| V040-UI-001 | P2 | UI | Partially implemented / Actions pending / UAT re-check pending | Add semantic color accents to workflow guidance |

## Name management workflow tabs

Implemented structure:

```text
Name Management
├─ 一覧
│  └─ name list and filtering only
├─ 新規追加
│  └─ clean add form that does not inherit selected rows
├─ 編集
│  └─ update form that requires explicit row selection
├─ 削除
│  └─ admin-oriented destructive workflow isolated from normal operations
└─ ガイド
   └─ operation rules and role restrictions
```

## Visibility / color direction

Current first step:

| Workflow | Accent |
|---|---|
| 一覧 | blue |
| 新規追加 | green |
| 編集 | indigo/purple |
| 削除 | red |
| ガイド | purple |

Future step:

- Move local accent style constants into shared UI style helpers.
- Apply the same semantic accent rules to title/subtitle management.
- Tune disabled button contrast if UAT still finds it unclear.

## Acceptance criteria

| ID | Criteria | Status |
|---|---|---|
| UX-NAME-001 | Name management has `一覧 / 新規追加 / 編集 / 削除 / ガイド` tabs. | Implemented / re-check pending |
| UX-NAME-002 | New-add form does not inherit the previously selected row. | Implemented / re-check pending |
| UX-NAME-003 | Edit requires explicit selection before update. | Implemented / re-check pending |
| UX-NAME-004 | Delete is isolated from normal add/edit flow. | Implemented / re-check pending |
| UX-NAME-005 | viewer/editor/admin role guards remain intact. | Implemented / Actions pending |
| UI-COLOR-001 | Workflow guidance uses visibly distinct semantic colors. | Partially implemented / re-check pending |
| UI-COLOR-002 | Semantic color implementation is shared across screens. | Not implemented |

## Implementation notes

- Updated `app/ui/name_management_tab.py`.
- Updated `tests/test_name_management_tab_ui.py`.
- Updated `tests/test_name_native_list_first_layout.py`.
- The shared color helper update was postponed after an attempted broad shared-style update was blocked by tooling safety checks.
- Local semantic color accents were added inside the name management tab as the first safe step.

## Release decision

Do not start release preparation until:

1. GitHub Actions passes for the name workflow tab implementation.
2. UAT re-check confirms the name tab workflow separation is acceptable.
3. Title/subtitle workflow tab implementation and UAT re-check are also acceptable.

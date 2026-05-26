# 94_title_subtitle_ui_redesign_backlog_20260526.md

## Purpose

This document records the UAT finding that the title/subtitle management area is too cluttered and not intuitive enough.

This is a release-affecting UX backlog item. It does not publish a release and does not complete UAT by itself.

## UAT finding

| Item | Value |
|---|---|
| Finding ID | UAT-F-003 |
| Severity | fix before release |
| Area | Title / Subtitle management UI |
| Summary | The title/subtitle area is too cluttered and difficult to operate intuitively. |
| Reported during | UAT viewer/editor/admin screen review |
| Release impact | Release preparation should remain deferred until this is either fixed and re-checked or explicitly accepted. |

## Observed pain points

| Pain point | Notes |
|---|---|
| Too many concepts in one screen | Title list, title form, subtitle list, subtitle form, related name selection, and destructive actions compete for attention. |
| Operation order is unclear | It is not immediately obvious whether to start from title selection, title creation, subtitle creation, or related name selection. |
| Visual hierarchy is weak | The primary workflow and secondary/destructive workflows are not separated enough. |
| Role-specific affordance is still noisy | viewer/editor/admin restrictions are visible, but the title/subtitle workflow itself remains hard to parse. |
| List-first change helped structure but not enough | The screen still needs workflow-level redesign, not only widget reordering. |
| Selection state persistence is annoying | Once a title is selected, the selected state remains even when the user expects a clean unselected/add mode. |
| Create/edit/delete are mixed | Listing, editing, deleting, and adding new records should be separated by workflow, not shown as one crowded panel. |

## First fix result

The first fix used **Option C: Master-detail layout**.

Implemented structure:

```text
Title/Subtitle Management
├─ Top: workflow hint
├─ Left: title list and reload only
└─ Right: selected-title workflow
   ├─ selected title details / create-update controls
   └─ subtitle list and create-update controls for the selected title
```

UAT re-check feedback: **not sufficient**.

Reason:

- The UI is cleaner than before but still keeps listing/editing/add/delete concepts too close together.
- Selection state continues to affect the user's mental model.
- The user explicitly prefers tabs such as list / edit / delete / new add.

## Revised target UX direction

Use workflow-level tab separation as the next implementation direction.

Recommended tab model:

```text
Title/Subtitle Management
├─ 一覧
│  └─ title/subtitle reference and selection preview only
├─ 新規追加
│  └─ create title / create subtitle flows without persistent edit selection noise
├─ 編集
│  └─ select existing title/subtitle, then update fields
├─ 削除
│  └─ admin-only delete/restore/hard-delete workflow, visually isolated
└─ ガイド
   └─ operation rules and role restrictions
```

## Candidate redesign options

| Option | Summary | Decision |
|---|---|---|
| A: Two sub-tabs | Split into `タイトル` and `サブタイトル` only. | Not enough; workflow separation is still weak. |
| B: Wizard-like flow | Step 1 select/create title, step 2 manage subtitles. | Useful later, but slower for power users. |
| C: Master-detail layout | Left title list, right selected-title details and subtitles. | Implemented first; UAT judged insufficient. |
| D: Collapse sections | Add collapsible create/update/destructive panels. | Not enough; still crowded. |
| E: Workflow tabs | Split into `一覧` / `新規追加` / `編集` / `削除` / `ガイド`. | Revised recommended direction. |

## Implementation status

| ID | Priority | Area | Status | Candidate |
|---|---:|---|---|---|
| V040-UX-002 | P2 | UI | Revision required / fix before release | Redesign title/subtitle management into workflow tabs |

## Acceptance criteria

| ID | Criteria | Status |
|---|---|---|
| UX-TS-001 | A user can identify whether they are in list, add, edit, or delete mode. | Revision required |
| UX-TS-002 | Selecting a row in list mode does not unexpectedly force edit/delete mode. | Revision required |
| UX-TS-003 | New-add flow starts from a clean form and is not polluted by previous selection state. | Revision required |
| UX-TS-004 | Edit flow requires explicit selection of an existing title/subtitle. | Revision required |
| UX-TS-005 | Delete/restore/hard-delete are isolated from normal create/update work. | Revision required |
| UX-TS-006 | Viewer can browse list/guide without seeing primary disabled write buttons as the main experience. | Revision required |
| UX-TS-007 | Editor sees add/edit as primary workflows and admin-only delete workflow remains separated. | Revision required |
| UX-TS-008 | Admin can access delete/restore/hard-delete from the delete tab only. | Revision required |
| UX-TS-009 | Tests assert workflow tabs and mode isolation. | Revision required |

## Decision

Do not start release preparation until one of the following is true:

1. Workflow-tab redesign is implemented and UAT re-check passes.
2. The user explicitly accepts the current title/subtitle UI as a known limitation for the release.

Current recommendation: implement workflow tabs before continuing release judgment.

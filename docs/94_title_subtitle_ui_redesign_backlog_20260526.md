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

## Target UX direction

| Direction | Description |
|---|---|
| Split by workflow | Separate title operations and subtitle operations more clearly. |
| Make selection state explicit | Show "selected title" as a persistent context header before subtitle operations. |
| Reduce simultaneous controls | Hide or collapse advanced/destructive controls unless needed. |
| Make create/update mode explicit | Use mode labels or separated panels so users know whether they are creating or editing. |
| Keep destructive actions away | Delete/restore/hard-delete should stay visually separated from normal create/update. |
| Improve empty-state guidance | When no title is selected, subtitle area should clearly say what to do next. |

## Candidate redesign options

| Option | Summary | Pros | Cons |
|---|---|---|---|
| A: Two sub-tabs | Split into `タイトル` and `サブタイトル` sub-tabs inside the management tab. | Simple mental model, less clutter per screen. | Cross-context operations need tab switching. |
| B: Wizard-like flow | Step 1 select/create title, step 2 manage subtitles. | Strong guidance for new users. | Slower for power users. |
| C: Master-detail layout | Left title list, right selected-title details and subtitles. | Common desktop pattern, good context. | Requires careful layout tuning. |
| D: Keep current layout but collapse sections | Add collapsible create/update/destructive panels. | Least disruptive. | May still feel crowded. |

## Implemented first fix

Used **Option C: Master-detail layout** as the first implementation.

Implemented structure:

```text
Title/Subtitle Management
├─ Top: workflow hint
├─ Left: title list and reload only
└─ Right: selected-title workflow
   ├─ selected title details / create-update controls
   └─ subtitle list and create-update controls for the selected title
```

## Implementation status

| ID | Priority | Area | Status | Candidate |
|---|---:|---|---|---|
| V040-UX-002 | P2 | UI | Implemented / Actions pending / UAT re-check pending | Redesign title/subtitle management into clearer master-detail workflow |

## Implementation notes

- Updated `app/ui/title_subtitle_management_tab.py`.
- Added top-level workflow hint.
- Left panel is now title-list focused.
- Right panel now contains selected title detail and selected-title subtitle management.
- Added `master_detail_layout` property for UI tests.
- Updated `tests/test_title_subtitle_management_tab_ui.py` to assert the master-detail structure.

## Acceptance criteria

| ID | Criteria | Status |
|---|---|---|
| UX-TS-001 | A user can identify the selected title without reading the whole form. | Implemented / re-check pending |
| UX-TS-002 | Subtitle operations are visually tied to the selected title. | Implemented / re-check pending |
| UX-TS-003 | Create/update/destructive actions are visually separated. | Partially implemented / re-check pending |
| UX-TS-004 | Viewer sees the structure without being distracted by unusable controls. | Implemented / re-check pending |
| UX-TS-005 | Editor can create/update without encountering admin-only destructive controls as primary actions. | Implemented / re-check pending |
| UX-TS-006 | Admin can still access delete/restore/hard-delete, but they are clearly separated. | Partially implemented / re-check pending |
| UX-TS-007 | Existing tests for role guards and list-first ordering are updated or replaced with layout-level tests. | Implemented / Actions pending |

## Decision

Do not start release preparation until one of the following is true:

1. `V040-UX-002` passes GitHub Actions and UAT re-check.
2. The user explicitly accepts the current title/subtitle UI as a known limitation for the release.

Current recommendation: run local re-check after pulling the latest implementation.

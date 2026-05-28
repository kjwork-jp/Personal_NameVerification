# 93_ui_acceptance_criteria_20260528.md

## 1. Purpose

This document defines acceptance criteria for the full UI/UX improvement backlog.

## 2. Global criteria

| ID | Criteria |
|---|---|
| AC-GLOBAL-001 | Screen purpose is understandable within 5 seconds. |
| AC-GLOBAL-002 | Primary action is visually clear. |
| AC-GLOBAL-003 | Destructive action is separated from normal action. |
| AC-GLOBAL-004 | Long UUIDs do not dominate primary views. |
| AC-GLOBAL-005 | Tables show important business fields first. |
| AC-GLOBAL-006 | Empty/unselected states explain the next action. |
| AC-GLOBAL-007 | Viewer/editor/admin state is visible. |
| AC-GLOBAL-008 | Guidance text is concise and does not crowd forms. |
| AC-GLOBAL-009 | All UI changes keep pytest, ruff, black, and mypy passing. |

## 3. Subtitle Management criteria

| ID | Criteria |
|---|---|
| AC-SUBTITLE-001 | List tab shows subtitles, not title rows. |
| AC-SUBTITLE-002 | Parent title summary is split into title name, public ID, and state. |
| AC-SUBTITLE-003 | Parent title can be found by partial word search. |
| AC-SUBTITLE-004 | Selected parent title is visible before creating or editing a subtitle. |
| AC-SUBTITLE-005 | Selected subtitle is visible before editing or deleting a subtitle. |
| AC-SUBTITLE-006 | Create/update button is enabled only when the required target/input is clear. |
| AC-SUBTITLE-007 | After create/update, the list reflects the latest subtitle values. |

## 4. Title Management criteria

| ID | Criteria |
|---|---|
| AC-TITLE-001 | Title edit screen is top-aligned and not dominated by blank space. |
| AC-TITLE-002 | Selected title summary is structured and readable. |
| AC-TITLE-003 | Related names are visible without making the form crowded. |

## 5. Login criteria

| ID | Criteria |
|---|---|
| AC-LOGIN-001 | Login screen shows app name and purpose. |
| AC-LOGIN-002 | Windows login and local login are visually separated. |
| AC-LOGIN-003 | Error and role guidance are visible and not cryptic. |

## 6. Tables criteria

| ID | Criteria |
|---|---|
| AC-TABLE-001 | Tables use readable widths and important columns first. |
| AC-TABLE-002 | Full IDs are available but not primary visual content. |
| AC-TABLE-003 | State is distinguishable as a badge/label, not only raw text. |
| AC-TABLE-004 | Row selection is visually clear. |

## 7. Release criteria

Final release readiness requires all P0/P1 items and their acceptance criteria to pass, plus completion or explicit deferral of P2/P3 items. Current scope requires P3 inclusion, so deferral is not assumed.

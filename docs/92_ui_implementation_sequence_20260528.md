# 92_ui_implementation_sequence_20260528.md

## 1. Purpose

This document turns `docs/91_full_ui_ux_backlog_20260528.md` into an implementation sequence.

## 2. Required principle

P3 items are included in the requested scope. They are not treated as optional unless the user explicitly changes the scope later.

## 3. Execution order

| Step | Work package | Primary backlog IDs | Exit criteria |
|---:|---|---|---|
| 0 | Restore green baseline | QG-RUFF-001 | Quality Gates pass. |
| 1 | Subtitle list correctness | UI-SUBTITLE-LIST-001, UI-SUBTITLE-LIST-002 | Subtitle list shows subtitles, not title list. |
| 2 | Subtitle parent-title card | UI-SUBTITLE-PARENT-001 | Parent title is split into title/public ID/state rows. |
| 3 | Subtitle flow redesign | UI-SUBTITLE-FLOW-001, UI-SUBTITLE-SEARCH-001, UI-SUBTITLE-EDIT-001 | Add/edit/delete flow is understandable. |
| 4 | Common table readability | UI-TABLE-001, UI-ID-001 | Dense tables and UUID dominance are reduced. |
| 5 | Title management redesign | UI-TITLE-EDIT-001, UI-TITLE-CONTEXT-001 | Title edit screen is usable and visually stable. |
| 6 | Login redesign | UI-LOGIN-001, UI-ROLE-001 | Login screen has product-level guidance and role visibility. |
| 7 | Navigation/forms/buttons/status | UI-NAV-001, UI-FORM-001, UI-BUTTON-001, UI-STATUS-001 | Main UI patterns are consistent. |
| 8 | Data I/O and logs | UI-DATAIO-001, UI-OPSLOG-001, UI-AUDIT-001 | Operational screens are readable and safe. |
| 9 | Help/settings/user management | UI-USER-001, UI-HELP-001 | Admin/help screens are readable. |
| 10 | P3 polish/hardening | UI-DESIGN-SYSTEM-001 through UI-RELEASE-POLISH-001 | UI polish scope is implemented and documented. |
| 11 | Final docs/UAT/release decision | DOC-STATUS-001, V100-REL-001 | Docs synchronized and final release readiness judged. |

## 4. Current immediate action

Start with Step 0: resolve current Quality Gates ruff failure after the subtitle-list replacement commit.

Then proceed to Step 2 and Step 3 because the user explicitly called out parent-title readability and subtitle-flow usability.

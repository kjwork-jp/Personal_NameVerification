# 94_ui_current_blockers_20260528.md

## 1. Current blockers

| ID | Type | Status | Details |
|---|---|---|---|
| QG-RUFF-001 | Quality Gate | RESOLVED | Green baseline restored. `122c04ce70db4cece313b1a717f15c78fbf0f601` passed `chatgpt/quality-gates` in run `26563517296`. |
| UI-SUBTITLE-LIST-001 | UI bug | FIX APPLIED / UAT REQUIRED | Subtitle list replacement is included in the current passing baseline. UAT must confirm the list shows subtitles, not title rows. |
| UI-SUBTITLE-PARENT-001 | UI readability | FIX APPLIED / UAT REQUIRED | Compatible parent-title summary labels were added. UAT must confirm title name, public ID, and state are split and readable. |
| UI-SUBTITLE-FLOW-001 | UX flow | FIX PARTIAL / UAT REQUIRED | Selected subtitle summary labels were added. UAT must confirm add/edit/delete flow is understandable. |
| UI-TABLE-001 | Common UI | IN PROGRESS | Readable table helper is applied to subtitle, name, trash, and audit tables. |
| UI-AUDIT-001 | Audit UI | FIX APPLIED / UAT REQUIRED | Audit renderer/export tests were aligned with the current pretty-JSON display, repr-style diff, and raw JSON export contract. `c5c59e717bb65bafd0eb763ee57301e575f7775a` passed `chatgpt/quality-gates` in run `26579008547`. |
| UI-LOGIN-001 | Login UI | OPEN | Login screen is too plain. |

## 2. Immediate next step

Proceed to `UI-LOGIN-001`: improve the login screen presentation while keeping role switching and credential handling unchanged.

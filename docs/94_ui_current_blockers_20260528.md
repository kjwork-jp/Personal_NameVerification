# 94_ui_current_blockers_20260528.md

## 1. Current blockers

| ID | Type | Status | Details |
|---|---|---|---|
| QG-RUFF-001 | Quality Gate | OPEN | Latest subtitle-list replacement commit failed ruff. pytest passed; ruff failed. |
| UI-SUBTITLE-LIST-001 | UI bug | FIX APPLIED / QG FAIL | Subtitle list replacement was implemented in `38dd7e6d394ae0e4a6e236f93bf7ae8483eaf901`, but Quality Gates must be restored. |
| UI-SUBTITLE-PARENT-001 | UI readability | OPEN | Parent title is still too dense and should be split into title/public ID/state rows. |
| UI-SUBTITLE-FLOW-001 | UX flow | OPEN | Subtitle add/edit/delete flow needs structured target-selection and selected-summary cards. |
| UI-TABLE-001 | Common UI | OPEN | Table design is still too mechanical. |
| UI-LOGIN-001 | Login UI | OPEN | Login screen is too plain. |

## 2. Immediate next step

Resolve QG-RUFF-001 first. No further implementation should be considered stable until Quality Gates are green again.

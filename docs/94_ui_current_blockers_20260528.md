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
| UI-LOGIN-001 | Login UI | FIX APPLIED / UAT REQUIRED | Login dialog presentation was improved with a page header, grouped Windows/local auth sections, clearer messages, and unchanged credential handling. `b1ff26a8ff79ace6c36c9138333acb8e5bb56598` passed `chatgpt/quality-gates` in run `26601487493`. |

## 2. Pending UAT checklist

### UI-LOGIN-001

| Check | Expected result | Evidence |
|---|---|---|
| Windows login | Windows authentication section is visible and login behavior is unchanged. | Screenshot of login dialog and successful main window. |
| Local login | Local authentication section is visible and Enter key login still works. | Screenshot or note with operator ID only. |
| Error message | Empty operator/password and invalid credential errors remain understandable. | Screenshot of each error message. |
| Role context | Main window still shows operator ID and role after login. | Screenshot of status bar or role banner. |

### UI-AUDIT-001

| Check | Expected result | Evidence |
|---|---|---|
| Before/after view | JSON values are readable as pretty JSON. | Screenshot of selected audit row details. |
| Diff view | Text diff uses repr-style value transitions. | Screenshot of diff area. |
| Invalid JSON fallback | Invalid JSON is shown as raw text without crashing. | Test data note or screenshot. |
| Export | Export preserves raw `before_json` and `after_json`. | Export file sample or checksum note. |

### UI-SUBTITLE-FLOW-001

| Check | Expected result | Evidence |
|---|---|---|
| Add flow | Selected parent title is obvious before adding subtitle. | Screenshot of add tab. |
| Edit flow | Selected subtitle and parent title are both visible before update. | Screenshot of edit tab. |
| Delete flow | Selected subtitle is visible before delete action. | Screenshot of delete tab. |
| Guard behavior | Deleted parent/subtitle cannot be updated. | Error message screenshot or test note. |

## 3. Immediate next step

Proceed to `UI-SUBTITLE-PARENT/LIST-UAT`: confirm the parent title fields are split into readable lines and the subtitle list shows subtitle rows, not title rows.

# 95_next_phase_workplan_20260530.md

## 1. Purpose

This document resets the workplan after the latest Data I/O UI slices reached a green Quality Gates state.

The remaining work is no longer feature implementation first. The next phase is:

1. Confirm latest Quality Gates for the final Data I/O commit.
2. Run focused UAT against the improved UI.
3. Update release evidence and status documents.
4. Decide release readiness or define any new follow-up defects.

## 2. Current baseline used for this plan

| Area | Current state |
|---|---|
| Subtitle list / parent display / flow | Fixes are implemented, but UAT evidence is still required. |
| Login | Improved and covered by UAT checklist, but manual evidence is still required. |
| Audit | Pretty JSON / diff / export contract is implemented, but manual evidence is still required. |
| Data I/O | S1 to S4 implementation and tests have been added. Final Quality Gates must be confirmed for the latest commit. |
| docs/91 | Older master backlog. Useful as historical scope, but no longer accurate as the active remaining-work list. |
| docs/94 | Current active blocker/UAT checklist source. |

## 3. Action accounting rule

| Rule | Treatment |
|---|---|
| Main implementation/UAT/doc-sync task | Counts toward the per-action difficulty limit. |
| Confirmation, status lookup, SHA lookup, small notes, manifest/status summarization | Does not count toward the difficulty limit, but is tracked as an out-of-limit reference value. |
| Per-action difficulty limit | 12. |
| Difficulty scale | 10 means must be executed alone. 1 means up to about 10 can be batched. |

## 4. Remaining work breakdown

| ID | Priority | Difficulty | Status | Scope | Acceptance criteria |
|---|---:|---:|---|---|---|
| QG-DATAIO-FINAL | P0 | 1 | Pending | Confirm Quality Gates for the latest Data I/O S4 commit. | `chatgpt/quality-gates` is success. |
| UAT-DATAIO-001 | P0 | 5 | Pending | Manual UAT for Data I/O guide, group descriptions, result hint, and Operations Log hint. | Screenshots or notes confirm no regression to Export/Backup/Restore/Import/log behavior. |
| UAT-SUBTITLE-001 | P0 | 4 | Pending | Manual UAT for subtitle list, parent title split display, and add/edit/delete target clarity. | Evidence confirms subtitle rows are shown and parent/title/subtitle context is readable. |
| UAT-LOGIN-001 | P1 | 3 | Pending | Manual UAT for Windows login, local login, validation errors, and role context display. | Evidence confirms login behavior is unchanged and UI is readable. |
| UAT-AUDIT-001 | P1 | 3 | Pending | Manual UAT for pretty JSON, repr-style diff, invalid JSON fallback, and raw export. | Evidence confirms audit details are readable and export preserves raw JSON. |
| DOC-SYNC-001 | P0 | 6 | Pending | Update docs/91 and docs/94 to reflect current completion and active UAT-only status. | Old completed blockers are marked resolved or superseded. |
| DOC-RELEASE-EVIDENCE-001 | P1 | 5 | Pending | Add final UAT / release-readiness evidence document. | Evidence references commits, Quality Gates, and manual UAT results. |
| RELEASE-READINESS-001 | P0 | 6 | Pending | Final release readiness decision. | Either release-ready, release-blocked with defects, or explicitly deferred scope is documented. |

## 5. Recommended execution sequence

### Action A: confirm final CI and prepare UAT sheet

| Task | Difficulty |
|---|---:|
| QG-DATAIO-FINAL | 1 |
| UAT-DATAIO-001 evidence template | 5 |
| UAT-SUBTITLE-001 evidence template | 4 |

Main difficulty: 10 / 12.

Out-of-limit reference work: status lookup, commit lookup, doc location lookup.

### Action B: remaining UAT evidence templates

| Task | Difficulty |
|---|---:|
| UAT-LOGIN-001 evidence template | 3 |
| UAT-AUDIT-001 evidence template | 3 |
| DOC-RELEASE-EVIDENCE-001 initial shell | 5 |

Main difficulty: 11 / 12.

### Action C: docs synchronization

| Task | Difficulty |
|---|---:|
| DOC-SYNC-001 | 6 |
| RELEASE-READINESS-001 draft decision matrix | 6 |

Main difficulty: 12 / 12.

### Action D: final decision

| Task | Difficulty |
|---|---:|
| RELEASE-READINESS-001 finalize after manual UAT results | 6 |

Main difficulty: 6 / 12.

## 6. Manual UAT evidence required from the local app

| Evidence ID | Screen | Required evidence |
|---|---|---|
| EV-DATAIO-01 | Data I/O > Guide | Header and role guide are visible. |
| EV-DATAIO-02 | Data I/O > Export / Backup / Restore / Import | Each operation tab shows the short description and existing controls still work. |
| EV-DATAIO-03 | Data I/O > Result area | Result hint appears above the output area, while OK/ERROR messages remain unchanged. |
| EV-DATAIO-04 | Data I/O > Operations Log | Log hint appears and filtering/paging/export remain available according to role. |
| EV-SUBTITLE-01 | Subtitle management | Subtitle list shows subtitle rows, not title rows. |
| EV-SUBTITLE-02 | Subtitle management | Parent title is split into title name, public ID, and state. |
| EV-SUBTITLE-03 | Subtitle management | Add/edit/delete target is clear before action. |
| EV-LOGIN-01 | Login | Windows and local login sections are visible. |
| EV-LOGIN-02 | Login/Main window | Role context appears after login. |
| EV-AUDIT-01 | Audit | Pretty JSON and diff views are readable. |
| EV-AUDIT-02 | Audit export | Raw JSON fields are preserved in export. |

## 7. Release readiness rule

Release readiness can be marked `READY` only when all of the following are true:

1. Latest Quality Gates are green.
2. Data I/O UAT passes.
3. Subtitle UAT passes.
4. Login UAT passes.
5. Audit UAT passes.
6. docs/91 and docs/94 no longer contradict the actual current state.
7. A final release evidence document exists.

If any item fails, the release state must be `BLOCKED` with defect IDs and next actions.

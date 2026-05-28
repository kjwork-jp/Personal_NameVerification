# 91_full_ui_ux_backlog_20260528.md

## 1. Purpose

This backlog consolidates all remaining fixes and improvements identified through the 2026-05-27 and 2026-05-28 UAT rounds for Personal_NameVerification.

Scope is no longer limited to release blockers. P3 and polish-level improvements are included as required work.

## 2. Current baseline

| Area | Current state |
|---|---|
| Core CRUD | Mostly functional, but UI quality and selection flow remain weak. |
| Related link unlink | Improved and treated as functionally passed in the latest UAT. |
| Subtitle management | Functional path is partially working, but list, parent-title display, selection flow, and readability require major improvement. |
| Title management | Functional path is partially working, but edit layout and information hierarchy remain weak. |
| Login | Functional, but visually too plain and lacks product-level guidance. |
| Tables | Too mechanical; long IDs, dense columns, weak hierarchy, weak state visibility. |
| Data I/O | Functional but dense; long paths and destructive-operation guidance need UI redesign. |
| Logs / audit | Developer-oriented; JSON/raw log readability is poor. |
| Documentation | docs/89, docs/90, docs/97 reflect part of the latest state; this backlog becomes the master list for remaining UI/UX work. |
| Quality Gates | Last fully passing code baseline before the latest subtitle-list fix: `6d9550f75dd1ecec32f9b7d9a2a084d8e76f6e48` / run `26549117150`. Latest subtitle-list fix `38dd7e6d394ae0e4a6e236f93bf7ae8483eaf901` still needs ruff failure resolution. |

## 3. Priority definitions

| Priority | Meaning |
|---|---|
| P0 | Blocks further validation or breaks basic screen semantics. Must be fixed immediately. |
| P1 | Required before final release readiness. Functionality or user comprehension is materially affected. |
| P2 | Required by the requested quality bar, but can be implemented after P0/P1 stabilization. |
| P3 | Polish / future-hardening level, now included in the requested full improvement scope. |

## 4. Master backlog

### P0: Immediate correctness / validation blockers

| ID | Area | Problem | Fix direction | Acceptance criteria |
|---|---|---|---|---|
| QG-RUFF-001 | Quality Gates | Commit `38dd7e6d394ae0e4a6e236f93bf7ae8483eaf901` fails ruff. | Read failing log or statically fix ruff-prone lines in subtitle list changes. | pytest / ruff / black / mypy all pass. |
| UI-SUBTITLE-LIST-001 | Subtitle Management / List | Subtitle Management > List displayed title rows / inherited title table semantics. | Replace list tab with subtitle-specific list. | List shows subtitle rows with parent title, subtitle code/name, state, order, updated_at, note. |
| UI-SUBTITLE-LIST-002 | Subtitle Management / List | Subtitle list refresh is fragile and not clearly tied to create/update. | Refresh after create/update and provide explicit reload button. | Newly created/updated subtitle appears after operation or reload. |

### P1: Required before final release readiness

| ID | Area | Problem | Fix direction | Acceptance criteria |
|---|---|---|---|---|
| UI-SUBTITLE-PARENT-001 | Subtitle Management | Parent title display is a long single line: `親タイトル タイトル: ...（公開ID... / 状態...）`. | Convert to structured summary card: title name, public ID, status. | Parent title info is split into separate visible rows. |
| UI-SUBTITLE-FLOW-001 | Subtitle Management | Add/edit/delete flow is hard to understand. | Rebuild as three sections: parent title selection, subtitle selection/list, edit content/action. | User can understand current target without reading table internals. |
| UI-SUBTITLE-SEARCH-001 | Subtitle Management | Editable combo alone does not feel like a working search. | Add explicit search field or robust searchable selector with auto-select and visible selected summary. | Partial title-name input finds/selects expected title. |
| UI-SUBTITLE-EDIT-001 | Subtitle Management | Editing depends on implicit table selection. | Add clear selected subtitle summary and stable form population. | Selected subtitle is obvious; edit button enables only when target is clear. |
| UI-TITLE-EDIT-001 | Title Management | Edit form is visually low / sparse / awkward. | Upper-align edit form; reduce dead space; improve selected title summary. | Title edit screen looks intentional and readable. |
| UI-TITLE-CONTEXT-001 | Title Management | Selected title context is verbose and hard to scan. | Structured title summary card with name, public ID, status, related names. | No dense one-line context strings. |
| UI-TABLE-001 | Common Tables | Tables are mechanical, dense, and expose long IDs too aggressively. | Create shared table-style helper: alternating rows, state labels, reasonable widths, tooltip full IDs. | Tables are readable without horizontal scanning for normal data. |
| UI-ID-001 | Common IDs | UUIDs dominate screen space. | Show short ID by default; full UUID in tooltip/details/copy. | Main tables/forms do not have full UUID as primary visual content. |
| UI-LOGIN-001 | Login | Login window is too plain. | Redesign as product landing/login screen with app title, purpose, Windows/local auth sections. | Login screen looks like the app entry point, not a default dialog. |
| UI-ROLE-001 | RBAC | Role differences are not visually explained enough. | Add role badge and allowed-operation summary. | Viewer/editor/admin state is clear at a glance. |
| DOC-STATUS-001 | Docs | docs/90/docs/97 need the new full backlog and UAT findings. | Cross-link this backlog and update status docs after implementation. | docs/90/docs/97 match current state. |

### P2: Required quality improvements

| ID | Area | Problem | Fix direction | Acceptance criteria |
|---|---|---|---|---|
| UI-NAV-001 | Main Navigation | Too many tabs; navigation feels crowded. | Group tabs into Data, Operations/Audit, Admin/Help or improve ordering. | User can predict where to go. |
| UI-COLOR-001 | Visual Design | Strong colored bands feel noisy. | Use calmer accents, badges, left borders, and spacing instead of heavy blocks. | Screens look less noisy while preserving warning hierarchy. |
| UI-FORM-001 | Forms | Forms lack consistent structure. | Standardize sections: target, input, action, result. | All CRUD screens follow a recognizable pattern. |
| UI-EMPTY-001 | Empty State | Blank/disabled states feel broken. | Add empty-state messages and next action guidance. | Unselected screens explain what to do next. |
| UI-BUTTON-001 | Buttons | Buttons are too mechanical and not prioritized. | Primary action emphasis; secondary actions smaller; destructive separated. | User can identify the next safe action. |
| UI-STATUS-001 | Status Bar / Messages | Long paths/status text are hard to scan. | Show concise message; full details in tooltip/copy/detail panel. | Important result is visible without reading long raw text. |
| UI-LINK-001 | Link Management | Functional but still mechanical. | Split unlinked candidates and existing links into cards/sections. | Register/unlink target is clear. |
| UI-DELETE-001 | Deleted Data | Danger UI is heavy and not refined. | Separate restore and hard delete; use confirmation card. | Destructive risk is clear without overwhelming red blocks. |
| UI-DATAIO-001 | Data I/O | Export/Backup/Restore/Import screens are dense. | Use path cards, browse/open/copy small actions, and clearer operation summaries. | User can identify selected path and operation risk. |
| UI-OPSLOG-001 | Operations Log | Operations log is raw/table-heavy. | Add type/result/target/detail columns and detail panel. | Logs are readable as operations evidence. |
| UI-AUDIT-001 | Audit Logs | Audit JSON before/after is hard to read. | Add formatted detail panel and diff-like display. | User can understand change without reading raw JSON. |
| UI-USER-001 | User Management | Role/status/auth provider are table-only. | Add badges and safer admin protection messaging. | User management is readable and safer. |
| UI-HELP-001 | Help / Settings | Long text is hard to consume. | Split into Help, Diagnostics, Paths, Protection Warnings. | Help/settings can be read without scrolling through dense text. |

### P3: Full polish / hardening scope

| ID | Area | Problem | Fix direction | Acceptance criteria |
|---|---|---|---|---|
| UI-DESIGN-SYSTEM-001 | UI Foundation | Each screen has ad-hoc styling. | Introduce shared UI helper for cards, badges, section headers, tables. | New screens share consistent look. |
| UI-RESPONSIVE-001 | Layout | Window resizing behavior is uneven. | Set sensible stretch factors, min widths, and scroll areas. | Screens remain usable at common laptop widths. |
| UI-COPY-001 | Copywriting | Labels are verbose or duplicated. | Standardize terminology: title name, public ID, state, parent title, selected subtitle. | Labels are short and consistent. |
| UI-ACCESSIBILITY-001 | Accessibility | Color is used too heavily as meaning. | Add text labels/icons/aria-like tooltips where relevant. | Meaning does not depend on color alone. |
| UI-KEYBOARD-001 | Keyboard Flow | Tab order and Enter behavior are not designed. | Review tab order and default buttons. | Common operations can be performed without mouse-heavy flow. |
| UI-SEARCH-001 | Search UX | Search behavior differs between screens. | Standardize searchable selector behavior. | Name/title/subtitle selectors behave consistently. |
| UI-DETAIL-PANE-001 | Details | Long values and notes are forced into tables. | Add reusable detail pane / selected record card. | Full details are available outside the table. |
| UI-CONFIRM-001 | Confirmations | Confirmation text is technical. | Use structured confirmation: target, action, consequence. | Dangerous operations are understandable. |
| UI-MICROCOPY-001 | Guidance | Guidance text is either too long or missing. | Add concise one-line microcopy per screen section. | Screens guide the next action without clutter. |
| UI-ERROR-001 | Errors | Error messages can be technical. | Normalize user-facing errors and keep trace details optional. | User sees actionable error text. |
| UI-SUCCESS-001 | Success feedback | Success state is weak. | Use consistent success messages and optional highlighted affected row. | User knows what changed. |
| UI-RELEASE-POLISH-001 | Release Package | UI polish is not reflected in release evidence. | Update docs/screenshots after UI revamp. | Release evidence matches actual improved UI. |

## 5. Implementation sequence

| Sprint | Scope | Goal |
|---|---|---|
| UI-0 | Fix current Quality Gates failure | Restore green baseline after subtitle-list fix. |
| UI-1 | Subtitle Management P0/P1 | Fix subtitle list, parent title card, selection/search/edit flow. |
| UI-2 | Common table and ID readability | Improve all table readability and UUID handling. |
| UI-3 | Title Management + Link Management | Make title edit and link screens consistent with new pattern. |
| UI-4 | Login + role/status polish | Improve first impression and role visibility. |
| UI-5 | Data I/O + Logs/Audit | Make operational screens readable and safer. |
| UI-6 | Help/Settings + P3 polish | Finish full UI/UX polish and documentation. |
| UI-7 | Final UAT/docs/release | Re-run UAT, update docs, decide release readiness. |

## 6. Immediate next actions

1. Resolve `QG-RUFF-001` for commit `38dd7e6d394ae0e4a6e236f93bf7ae8483eaf901` or a follow-up commit.
2. Implement `UI-SUBTITLE-PARENT-001` and `UI-SUBTITLE-FLOW-001`.
3. Add tests for subtitle list replacement and parent-title summary readability.
4. Confirm Quality Gates success through `chatgpt/quality-gates` commit status.
5. Update docs/90 and docs/97 to reference this backlog and the latest results.

## 7. Release readiness rule

Release preparation remains blocked until:

- Quality Gates are green.
- P0/P1 backlog items are implemented and re-UAT passes.
- P2/P3 scope is either implemented or explicitly deferred by a new user decision. Current user decision requires P3 inclusion, so deferral is not assumed.
- docs/72, docs/75, docs/88, docs/89, docs/90, docs/91, and docs/97 are synchronized.

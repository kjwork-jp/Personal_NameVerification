# 99_ui_polish_next_phase_plan_20260531.md

## 1. Purpose

This document decomposes the remaining post-READY UI polish work into concrete follow-up tasks.

These items are not release blockers. The current release readiness remains READY. This plan exists to avoid ambiguous catch-all backlog items such as `UI-POLISH-FOLLOWUP`.

## 2. Current state

| Area | State |
|---|---|
| Release readiness | READY |
| Active P0/P1 blockers | None |
| Data I/O UI | UAT PASS |
| Subtitle management UI | UAT PASS |
| Subtitle cross-parent search | Implemented and local pytest PASS |
| External ledgers | Reduced to minimal local control package; GitHub docs are source of truth |
| Local command index | Added as `docs/99_local_command_index_20260531.md` |

## 3. Already completed UI improvements

| ID | Status | Notes |
|---|---|---|
| DATAIO-GUIDANCE | DONE | Guide tab, operation descriptions, result hint, Operations Log hint. |
| SUBTITLE-LIST-REPLACEMENT | DONE | Subtitle-focused list replaces title-list confusion. |
| SUBTITLE-PARENT-SUMMARY | DONE | Parent title split into title name, public ID, and state. |
| SUBTITLE-SELECTED-SUMMARY | DONE | Edit/delete target subtitle is explicit. |
| CROSS-PARENT-SUBTITLE-SEARCH | DONE | List tab can search subtitles across parent titles. |
| SUBTITLE-TABLE-UX | DONE/PARTIAL | Tooltip and better list filtering were added for subtitle list. |

## 4. Remaining UI polish backlog

| ID | Priority | Difficulty | Scope | Acceptance criteria |
|---|---:|---:|---|---|
| TITLE-MANAGEMENT-POLISH | P2 | 5 | Improve the base title management edit/delete screens so selected title context is split and easier to read. | Selected title context is displayed as title name, public ID, state, and linked names rather than a dense one-line label. Existing title CRUD behavior remains unchanged. |
| TITLE-DELETE-DANGER-COPY | P2 | 3 | Improve destructive title operation labels and confirmation copy. | Delete/restore/hard-delete controls clearly state target and risk. No behavior change. |
| TABLE-UX-REMAINING | P2 | 3 | Apply table readability improvements beyond the subtitle list. | Long IDs do not dominate normal scanning; full IDs remain accessible via tooltip/detail. Status and order columns are visually scannable. |
| MICROCOPY-CONSISTENCY | P2 | 4 | Normalize Japanese/English mixed guidance and button labels. | User-facing guidance has a consistent language policy. Technical English remains only where useful, such as file formats. |
| NAVIGATION-POLISH | P3 | 4 | Revisit main tab ordering/grouping after current release. | Frequently used screens are easy to find; destructive/admin screens remain separated. |
| AUDIT-EXPORT-EVIDENCE-OPTIONAL | P2 | 2 | Optional evidence, not UI implementation. | Audit export evidence is captured if required later. |
| RELEASE-TAGGING | P2 | 3 | Optional packaging. | Tag/changelog references release readiness and final UAT evidence. |

## 5. Recommended execution sequence

### Action 1: title context readability

| Task | Difficulty |
|---|---:|
| TITLE-MANAGEMENT-POLISH | 5 |
| TITLE-DELETE-DANGER-COPY | 3 |

Main difficulty: 8 / 12.

Implementation guardrails:

- Do not change CRUD service calls.
- Do not change RBAC rules.
- Do not change DB schema.
- Add tests for selected-title summary text/properties.

### Action 2: table and microcopy consistency

| Task | Difficulty |
|---|---:|
| TABLE-UX-REMAINING | 3 |
| MICROCOPY-CONSISTENCY | 4 |

Main difficulty: 7 / 12.

Implementation guardrails:

- Keep current release-ready flows intact.
- Prefer properties/tests over visual-only changes.
- Avoid large theme rewrites.

### Action 3: navigation review

| Task | Difficulty |
|---|---:|
| NAVIGATION-POLISH | 4 |

Main difficulty: 4 / 12.

Implementation guardrails:

- Do not hide existing screens.
- Avoid reordering that breaks user muscle memory unless the improvement is explicit.
- Keep admin/destructive screens visibly separated.

## 6. Title management polish target design

Current issue:

- The base title/subtitle management screen still uses dense one-line title context in places.
- Subtitle-focused screen already improved context cards.
- The title-focused screen should follow the same target/input/action principle.

Target UI pattern:

```text
選択中タイトル
タイトル名  sample-title-0000017
公開ID      73890748-...
状態        有効
関連名      Alice, Bob
```

The full public ID should remain selectable/copyable or available in tooltip/detail.

## 7. Microcopy policy

| Category | Rule |
|---|---|
| Primary labels | Japanese. |
| File formats | Technical English allowed: CSV, JSON, SQL dump. |
| Result prefixes | Keep `[OK]` / `[ERROR]` because they are log-like status markers. |
| Destructive actions | Japanese with explicit risk: `ゴミ箱`, `復元`, `完全削除`. |
| Guidance | Short Japanese sentence first; detailed notes in guide/help sections. |

## 8. Current remaining work list

| ID | Priority | Difficulty | Owner | Status |
|---|---:|---:|---|---|
| TITLE-MANAGEMENT-POLISH | P2 | 5 | AI/dev | Pending |
| TITLE-DELETE-DANGER-COPY | P2 | 3 | AI/dev | Pending |
| TABLE-UX-REMAINING | P2 | 3 | AI/dev | Pending |
| MICROCOPY-CONSISTENCY | P2 | 4 | AI/dev | Pending |
| NAVIGATION-POLISH | P3 | 4 | AI/dev | Pending |
| AUDIT-EXPORT-EVIDENCE-OPTIONAL | P2 | 2 | User | Optional |
| RELEASE-TAGGING | P2 | 3 | AI/dev + User | Optional |

## 9. User-side commands after implementation

After future UI implementation commits:

```powershell
git pull --ff-only
python -m pytest -q
.\scripts\reset_uat_demo_windows.ps1 -Launch
```

For focused title/subtitle UI confirmation:

```powershell
python -m pytest tests/test_title_subtitle_management_tab_ui.py tests/test_subtitle_management_tab_ui.py -q
```

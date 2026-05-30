# 98_post_ready_followup_backlog_20260530.md

## 1. Purpose

This document defines the post-READY follow-up backlog after the final UAT and release readiness decision recorded on 2026-05-30.

The items here are not active release blockers. They are improvement candidates for the next phase.

## 2. Current state

| Item | Status |
|---|---|
| Release readiness | READY |
| Final release readiness document | `docs/97_final_release_readiness_20260530.md` |
| Final UAT evidence | `docs/96_final_uat_evidence_20260530.md` |
| Active release blockers | None |
| Required user-side work | Pull latest docs locally. |

## 3. Remaining work including user-side actions

| ID | Priority | Difficulty | Owner side | Status | Scope | Acceptance criteria |
|---|---:|---:|---|---|---|---|
| LOCAL-PULL-FINAL | P0 | 1 | User | Pending | Pull latest documentation commits to the local repository. | `git pull --ff-only` completes and local `main` includes docs/97 and docs/98. |
| AUDIT-EXPORT-EVIDENCE-OPTIONAL | P2 | 2 | User | Optional | Capture explicit audit export evidence if required. | Screenshot or file evidence proves audit export preserves raw JSON. |
| CROSS-PARENT-SUBTITLE-SEARCH | P2 | 4 | AI/dev | Optional enhancement | Allow cross-parent subtitle search/edit if future operation requires it. | User can search subtitles across parent titles without first selecting one parent title. |
| UI-POLISH-FOLLOWUP | P2 | 6 | AI/dev | Optional enhancement | Improve UI spacing, hierarchy, microcopy, and visual consistency across remaining screens. | Screens look consistent and less mechanical without changing core behavior. |
| TABLE-UX-REFINEMENT | P2 | 5 | AI/dev | Optional enhancement | Improve table columns, ID display, state badges, and row readability. | Long IDs do not dominate normal table scanning; full IDs remain accessible. |
| TITLE-MANAGEMENT-POLISH | P2 | 5 | AI/dev | Optional enhancement | Improve title edit/layout context and selected title summaries. | Title edit screen follows the clearer target/input/action pattern. |
| NAVIGATION-POLISH | P3 | 4 | AI/dev | Optional enhancement | Revisit main tab ordering/grouping if navigation still feels crowded. | Users can predict where to go without scanning every tab. |
| RELEASE-TAGGING | P2 | 3 | AI/dev + User | Optional packaging | Create release tag/changelog/package notes if a formal release artifact is needed. | Tag and changelog reference READY decision and final UAT evidence. |

## 4. Recommended next action groups

### Group A: local synchronization and optional evidence

| Task | Difficulty |
|---|---:|
| LOCAL-PULL-FINAL | 1 |
| AUDIT-EXPORT-EVIDENCE-OPTIONAL | 2 |

Main difficulty: 3 / 12.

### Group B: next UI improvement slice

| Task | Difficulty |
|---|---:|
| CROSS-PARENT-SUBTITLE-SEARCH | 4 |
| TABLE-UX-REFINEMENT | 5 |

Main difficulty: 9 / 12.

### Group C: polish planning

| Task | Difficulty |
|---|---:|
| UI-POLISH-FOLLOWUP | 6 |
| NAVIGATION-POLISH | 4 |

Main difficulty: 10 / 12.

### Group D: formal packaging

| Task | Difficulty |
|---|---:|
| RELEASE-TAGGING | 3 |
| TITLE-MANAGEMENT-POLISH plan only | 3 |

Main difficulty: 6 / 12.

## 5. User-side command reminder

When the user is ready to sync local files:

```powershell
git pull --ff-only
```

No virtualenv or `cd` command is repeated here because the user requested those steps be skipped.

## 6. Notes

- None of these follow-up items should change the READY decision unless a new defect is discovered.
- New defects should receive new IDs rather than reopening historical blocker rows.
- Optional work should remain clearly separated from release blockers.

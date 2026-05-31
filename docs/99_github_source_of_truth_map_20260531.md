# 99_github_source_of_truth_map_20260531.md

## 1. Purpose

This document defines which project information is managed in GitHub and which information remains in the local external ledger package.

## 2. Source of truth split

| Domain | Source of truth | External ledger treatment |
|---|---|---|
| Code | GitHub repository files | Commit/link reference only. |
| Tests | GitHub tests and GitHub Actions | Latest result summary only. |
| CI and Quality Gates | GitHub Actions | Latest pass/fail summary only. |
| Design decisions | GitHub docs | Link only. |
| UAT evidence summary | `docs/96_final_uat_evidence_20260530.md` | Status summary and received-evidence checklist only. |
| Release readiness | `docs/97_final_release_readiness_20260530.md` | Current READY/BLOCKED state only. |
| Follow-up backlog | `docs/98_post_ready_followup_backlog_20260530.md` | High-level index only. |
| External package receipt | Minimal external workbook | Local workbook owns this. |

## 3. Current GitHub documents

| Document | Owns |
|---|---|
| `docs/91_full_ui_ux_backlog_20260528.md` | Historical UI/UX backlog and resolved/accepted status. |
| `docs/94_ui_current_blockers_20260528.md` | Current blocker closure status. |
| `docs/95_next_phase_workplan_20260530.md` | Workplan after Data I/O UI work. |
| `docs/96_final_uat_evidence_20260530.md` | Final UAT evidence summary. |
| `docs/97_final_release_readiness_20260530.md` | READY decision. |
| `docs/98_post_ready_followup_backlog_20260530.md` | Post-READY follow-up backlog. |
| `docs/99_external_ledger_minimal_policy_20260531.md` | Minimal external ledger policy. |
| `docs/99_github_source_of_truth_map_20260531.md` | This source-of-truth map. |

## 4. Current local external-ledger package target

Current local package name:

`52_名前解決アプリ_外部台帳_最小構成_20260531.zip`

Expected contents:

| Path | Purpose |
|---|---|
| `00_README_外部台帳最小構成_20260531.md` | Explains minimal local ledger policy. |
| `01_外部台帳最小構成/NameVerification_外部管理ミニ台帳_20260531.xlsx` | Local control workbook. |
| `02_手元確認/NameVerification_v3_手元確認スクリプト集_20260531.docx` | Local verification command manual. |
| `99_manifest/manifest_20260531.csv` | Package manifest. |
| `99_manifest/checksums_sha256_20260531.txt` | Checksums. |

## 5. Current active follow-ups

| ID | Priority | Treatment |
|---|---:|---|
| UI-POLISH-NEXT-PHASE | P2 | Follow-up, not release blocker. |
| TITLE-MANAGEMENT-POLISH | P2 | Follow-up, not release blocker. |
| NAVIGATION-POLISH | P3 | Follow-up, not release blocker. |
| TABLE-UX-REMAINING | P2 | Follow-up, not release blocker. |
| MICROCOPY-CONSISTENCY | P2 | Follow-up, not release blocker. |
| AUDIT-EXPORT-EVIDENCE-OPTIONAL | P2 | Optional evidence. |
| RELEASE-TAGGING | P2 | Optional packaging. |
| PARENT-TITLE-COUNT-AUDIT | P2 | Optional local audit. |

## 6. Rule

Detailed history must be updated in GitHub first. The external workbook should stay small and only point to the relevant GitHub documents.

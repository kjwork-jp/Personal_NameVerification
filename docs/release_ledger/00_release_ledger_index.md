# NameVerification release / development ledger index

## Purpose

This page is the entry point for release evidence, implementation ledgers, backlog records, and development handoff notes.

User-facing manuals are intentionally separated under `docs/manuals/00_user_manual_index.md`.

## Stable baseline

- Current stable baseline: v0.2.0
- Next development target: v0.3.0
- Main backlog index: `docs/85_v0_3_0_backlog_initial_20260525.md`

## Release evidence

| Scope | Document |
|---|---|
| v0.2.0 stable release | `docs/83_release_final_v0_2_0_20260525.md` |
| v0.2.0 scope / final state | `docs/80_v0_2_0_pre_zip_scope_update_20260523.md` |
| v0.2.0-rc2 history | `docs/81_release_final_v0_2_0_rc2_20260525.md` |
| v0.1.0-rc2 history | `docs/59_release_evidence_v0_1_0_rc2.md` |

## Project ledgers

| Scope | Document |
|---|---|
| v0.3.0 backlog | `docs/85_v0_3_0_backlog_initial_20260525.md` |
| v0.2.0 status ledger | `docs/75_v0_2_0_current_status_and_improvement_ledger.md` |
| Open issues and constraints | `docs/97_open_issues_and_constraints.md` |
| RBAC hardening plan | `docs/74_rbac_hardening_plan.md` |
| UI navigation redesign plan | `docs/73_ui_navigation_redesign_plan.md` |

## CI / release automation

| Area | File |
|---|---|
| Lightweight quality gate | `.github/workflows/quality-gates.yml` |
| Manual Windows validation | `.github/workflows/windows-validation.yml` |
| Manual Windows EXE build | `.github/workflows/windows-exe.yml` |
| Manual release dry-run | `.github/workflows/release-dry-run.yml` |
| Release orchestration | `scripts/run_release_windows.ps1` |
| Release checklist generator | `scripts/generate_release_checklist_windows.ps1` |

## Reading rule

- End users should start from `docs/manuals/00_user_manual_index.md`.
- Developers and release operators should start from this page.
- Release evidence should not be copied into user-facing manuals unless it changes user operation.

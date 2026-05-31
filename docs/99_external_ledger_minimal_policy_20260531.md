# 99_external_ledger_minimal_policy_20260531.md

## 1. Decision

External hand-managed ledgers must be kept minimal.

The project source of truth is GitHub. External ledgers are retained only as a local control/index layer for handoff, offline review, and artifact receipt confirmation.

## 2. Rationale

Previous external-ledger packages became too large because they attempted to duplicate all project history, design, UAT, evidence, WBS, release status, and follow-up backlog in spreadsheets.

That approach creates several problems:

1. duplicated truth between GitHub docs and external XLSX files;
2. high update cost after every commit;
3. risk of stale ledger rows;
4. difficulty distinguishing current blockers from historical notes;
5. large ZIP packages that are harder to review manually.

Therefore, from this point forward:

- GitHub manages detailed history, design, UAT, release decisions, and follow-up backlog.
- External ledger files manage only local control, index, receipt, status summary, and review checklist.

## 3. GitHub-managed source of truth

| Area | GitHub source |
|---|---|
| UI backlog / historical blocker status | `docs/91_full_ui_ux_backlog_20260528.md` |
| UAT and next-phase workplan | `docs/95_next_phase_workplan_20260530.md` |
| Final UAT evidence | `docs/96_final_uat_evidence_20260530.md` |
| Release readiness decision | `docs/97_final_release_readiness_20260530.md` |
| Post-READY follow-up backlog | `docs/98_post_ready_followup_backlog_20260530.md` |
| External ledger minimal policy | `docs/99_external_ledger_minimal_policy_20260531.md` |
| GitHub source-of-truth map | `docs/99_github_source_of_truth_map_20260531.md` |

## 4. External ledger minimal scope

The local external-ledger package should contain only:

1. a minimal control workbook;
2. local verification script manual if needed;
3. manifest and checksum;
4. README that points to GitHub docs.

It should not duplicate full WBS, full UAT history, full design history, or full artifact inventory when those are already maintained in GitHub.

## 5. External ledger required sheets

The minimal control workbook should have these sheets:

| Sheet | Purpose |
|---|---|
| `00_README` | Local package purpose and GitHub source-of-truth policy. |
| `01_STATUS_INDEX` | Current status, READY decision, latest commit, latest local verification. |
| `02_LOCAL_ACTIONS` | User-side commands and local review actions. |
| `03_GITHUB_SOT_MAP` | Pointers to GitHub docs and what each doc owns. |
| `04_FOLLOWUP_INDEX` | Only high-level follow-up IDs and whether they are blocker/optional. |
| `05_RECEIPT_LOG` | When the local package was received/reviewed. |

## 6. Update rule

When a future change occurs:

1. Update detailed project facts in GitHub docs first.
2. Update the external workbook only if local handoff/control state changes.
3. Do not expand the external workbook into a second full project database.
4. If a row needs detailed explanation, link to the GitHub doc instead of duplicating text.

## 7. Current release state

| Item | State |
|---|---|
| Release readiness | READY |
| Active P0/P1 app blockers | None |
| Latest cross-parent subtitle search local pytest | PASS: `python -m pytest tests/test_subtitle_management_tab_ui.py -q` |
| UI polish | Follow-up only, not release blocking |

# 85_v0_3_0_backlog_initial_20260525.md

## Baseline

- Stable baseline: v0.2.0
- Stable release status: complete
- Required v0.2.0 P1 items: complete
- Current development line: v0.3.0+
- Latest `Quality Gates`: success for PR #184 exact head and merge commit `325244defdf9658f5ea16c9550fcd73d8c5aefc6`

## Backlog references

| Scope | Document |
|---|---|
| Immediate v0.3.x work | this file |
| Future roadmap / remaining backlog | `docs/86_future_roadmap_and_remaining_backlog_20260525.md` |
| Open issues / constraints | `docs/97_open_issues_and_constraints.md` |
| Release/development ledger index | `docs/release_ledger/00_release_ledger_index.md` |

## Current state

- Original implementation and maintenance backlog is complete.
- PR #184 is merged and its main-branch quality gate passed.
- Issue #110 was closed because its v0.1.0-rc1 line is superseded by v0.2.0 and v0.3.0+.
- Open PR: 0.
- Open Issue: 0.
- Manual UAT, EXE checks, portable checks, local Windows builds, and release publishing are not normal active backlog items.

## Remaining candidates requiring re-audit

| Priority | Candidate | Status |
|---|---|---|
| P1 | datetime helper未適用画面 | 未監査候補 |
| P1 | title edit UI崩れ | 未監査候補 |
| P1 | audit log diff display | 未監査候補 |
| P1 | Data I/O wording / Japanese | 未監査候補 |
| P1 | title list name filter | 未監査候補 |
| P1 | unlink granularity | 未監査候補 |
| P2 | list columns reduction and detail pane | design候補 |
| P2 | subtitle-first editing | design候補 |
| P2 | search single table and detail pane | design候補 |

Old handoff candidates must be checked against current code, tests, screenshots, Issues, and Actions before they are treated as defects or implementation work.

## Next action

Re-audit the P1 candidates and create or implement only confirmed gaps. Do not reactivate completed work or historical release gates.

# 85_v0_3_0_backlog_initial_20260525.md

## Baseline

- Stable baseline: v0.2.0
- Stable release status: complete
- Required v0.2.0 P1 items: complete
- Current development line: v0.3.0+
- Latest `Quality Gates`:
  - PR #184: success (exact-head & main merge `325244defdf9658f5ea16c9550fcd73d8c5aefc6`)
  - PR #185: success on exact-head (`5b59223119d74403ad619f71b8ff6ed4e6bc8d06`, run `27539109959`) and main merge (`0eeaf869de745f5d487ba5bebfb786669fb4ee20`, run `27539233424`)

## Backlog references

| Scope | Document |
|---|---|
| Immediate v0.3.x work | this file |
| Future roadmap / remaining backlog | `docs/86_future_roadmap_and_remaining_backlog_20260525.md` |
| Open issues / constraints | `docs/97_open_issues_and_constraints.md` |
| Release/development ledger index | `docs/release_ledger/00_release_ledger_index.md` |

## Current state

- Original implementation and maintenance backlog is complete.
- PR #184 (`feat: enforce normalized display-name indexes`) is merged (squash, merge commit `325244defdf9658f5ea16c9550fcd73d8c5aefc6`).
- PR #185 (`fix(ui): close audited P1 usability gaps`) is merged (squash, merge commit `0eeaf869de745f5d487ba5bebfb786669fb4ee20`).
- Issue #110 was closed because its v0.1.0-rc1 line is superseded by v0.2.0 and v0.3.0+.
- Open PR: 0.
- Open Issue: 0.
- Manual UAT, EXE checks, portable checks, local Windows builds, and release publishing are not normal active backlog items.
- P1候補6件はPR #185で監査・修正/実装済み。

## Remaining candidates requiring re-audit

| Priority | Candidate | Status |
|---|---|---|
| P1 | datetime helper未適用画面 | 2026-06-15監査・修正済み |
| P1 | title edit UI崩れ | 2026-06-15監査・修正済み |
| P1 | audit log diff display | 2026-06-15監査・修正済み |
| P1 | Data I/O wording / Japanese | 2026-06-15監査・修正済み |
| P1 | title list name filter | 2026-06-15監査・実装済み |
| P1 | unlink granularity | 2026-06-15監査・実装済み |
| P2 | list columns reduction and detail pane | design候補 |
| P2 | subtitle-first editing | design候補 |
| P2 | search single table and detail pane | design候補 |

Old handoff candidates must be checked against current code, tests, screenshots, Issues, and Actions before they are treated as defects or implementation work.

## Next action

P1候補6件はPR #185で完了。次の確定候補はP2 design 3件:
1. list columns reduction + detail pane (UI-DESIGN-01)
2. subtitle-first editing (UI-DESIGN-02)
3. search single table + detail pane (UI-DESIGN-03)

Re-audit `docs/67_quality_attribute_gap_analysis.md` の `requires re-audit` items against current code/tests.
Manual UAT / release publishing は deferred explicit gates として自動的な次工程にしない。

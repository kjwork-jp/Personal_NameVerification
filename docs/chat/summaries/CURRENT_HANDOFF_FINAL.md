# Personal_NameVerification 最終引継ぎ入口

更新日: 2026-06-15

GitHubのlive stateを一次情報として扱ってください。Google Driveは基本参照しません。

## 現在地点

PR #185 `fix(ui): close audited P1 usability gaps` は完了済みです。

- merge方式: squash
- merge commit: `0eeaf869de745f5d487ba5bebfb786669fb4ee20`
- merge前head: `5b59223119d74403ad619f71b8ff6ed4e6bc8d06`
- exact-head Quality Gates: success (run `27539109959`)
- merge後main Quality Gates: success (run `27539233424`)
- review thread: 0件

### PR #184 (前回merge)

- merge方式: squash
- merge commit: `325244defdf9658f5ea16c9550fcd73d8c5aefc6`
- merge前head: `adc3e4418900eb939a37383847ce5892e8354e77`
- exact-head Quality Gates: success
- merge後main Quality Gates: success (run `27526922774`)

## PR #185 changed scope

PR #185で監査・修正/実装したP1候補6件:

- datetime helper未適用画面 → 監査・修正済み
- title edit UI崩れ → 監査・修正済み
- audit log diff display → 監査・修正済み
- Data I/O wording / Japanese → 監査・修正済み
- title list name filter → 監査・実装済み
- unlink granularity → 監査・実装済み

changed files: 21件 (app/ui/*.py 11件, tests/*.py 9件, docs/85*.md 1件)

## open PR / Issue

2026-06-15同期時点:

- open PR: 0件
- open Issue: 0件
- Issue #110はstable v0.2.0 / current v0.3.0+ によりsupersededとして理由コメント付きでclose済み

## 次の開発候補

P1候補6件はPR #185で完了済み。

### P2 / design候補 (current confirmed)

| ID | Candidate | Status |
|---|---|---|
| UI-DESIGN-01 | list columns reduction + detail pane | design候補 |
| UI-DESIGN-02 | subtitle-first editing | design候補 |
| UI-DESIGN-03 | search single table + detail pane | design候補 |

これらはdesign候補であり、古い文書だけを根拠に現行不具合と断定しません。

### Requires re-audit

- `docs/67_quality_attribute_gap_analysis.md` の `requires re-audit` items (18件)
- password policy (CONF-005), destructive re-auth (CONF-008), audit log role separation (CONF-009) 等

### Deferred explicit gates

- 人間UAT (V900-UAT-001)
- release publish (V100-REL-001)

これらは通常残工程へ入れず、明示的な人間判断を必要とする。

## 運用

- CI未通過PRはmergeしない
- review未解決PRはmergeしない
- mergeableがfalse / unknown / nullのPRはmergeしない
- exact-head CI successを確認する
- merge方式は原則squash、expected head SHAを指定する
- merge後main Quality Gatesを確認する
- 人間の手元UAT / EXE / portable確認を通常残工程へ入れない
- 完了済みを残工程へ再掲しない
- 追加Secretは不要
- UATとrelease publishはdeferred explicit gatesであり、自動的な次工程にしない

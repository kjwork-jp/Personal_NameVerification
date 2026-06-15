# Personal_NameVerification 最終引継ぎ入口

更新日: 2026-06-15

GitHubのlive stateを一次情報として扱ってください。Google Driveは基本参照しません。

## 現在地点

PR #184 `feat: enforce normalized display-name indexes` は完了済みです。

- merge方式: squash
- merge commit: `325244defdf9658f5ea16c9550fcd73d8c5aefc6`
- merge前head: `adc3e4418900eb939a37383847ce5892e8354e77`
- exact-head Quality Gates #299: success
- review threads: 5件すべてresolve済み
- merge後main Quality Gates: success
- merge後run ID: `27526922774`

main側のhandoff更新によるbehind 1は、PR変更ファイルと重複しないdocs-only差分でした。GitHub live評価で`mergeable=true`を再確認してからexpected head SHA指定でmergeしています。

## open PR / Issue

2026-06-15同期時点:

- open PR: 0件
- open Issue: 0件
- Issue #110はstable v0.2.0 / current v0.3.0+ によりsupersededとして理由コメント付きでclose済み

## 次の開発候補

古いhandoff由来の候補は、現行code / tests / screenshotsで再監査してからIssue化または実装してください。

P1候補:

- datetime helper未適用画面
- title edit UI崩れ
- audit log diff display
- Data I/O wording / Japanese
- title list name filter
- unlink granularity

P2 / design候補:

- list columns reduction + detail pane
- subtitle-first editing
- search single table + detail pane

これらは未監査候補であり、古い文書だけを根拠に現行不具合と断定しません。

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

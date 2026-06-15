# Personal_NameVerification 最終引継ぎ入口

更新日: 2026-06-15

GitHubのlive stateを一次情報として扱ってください。Google Driveは基本参照しません。

## 現在地点

最優先はPR #184 `feat: enforce normalized display-name indexes` です。

- PR: https://github.com/kjwork-jp/Personal_NameVerification/pull/184
- branch: `feat/display-name-expression-indexes`
- 確認済みhead: `adc3e4418900eb939a37383847ce5892e8354e77`
- Quality Gates #299: success
- review threads: 5件すべてresolve済み
- 確認時: open / mergeable=true / 未merge

この文書更新でmainが進むため、PR #184のbase/head、mergeable、exact-head CI、未解決threadを再取得してください。

条件がそろえばexpected head SHAを指定してsquash mergeし、merge後main CIとopen PR/Issueを再監査してください。

## 後続

open Issueは#110のみです。stable v0.2.0公開済み・現行開発線v0.3.0+と照合し、superseded/completedとしてclose可能か判断してください。

## 運用

- CI未通過PRはmergeしない
- review未解決PRはmergeしない
- 人間の手元UAT/EXE/portable確認を通常残工程へ入れない
- merge方式は原則squash
- 完了済みを除いた残工程一覧を毎回出す
- 追加Secret、1Password、OP_SERVICE_ACCOUNT_TOKENは不要

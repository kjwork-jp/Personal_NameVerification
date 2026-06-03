# Personal_NameVerification / 名前解決アプリ 最終引継ぎ入口

作成日: 2026-06-03
対象repo: `kjwork-jp/Personal_NameVerification`

このファイルは、新規チャットへ作業を引き継ぐための最終入口です。

## 参照する詳細文書

- 詳細正本: `docs/chat/summaries/20260603_personal_nameverification_handoff_detail.md`
- 旧入口: `docs/chat/summaries/CURRENT_HANDOFF.md`
- 初回プロンプト履歴: `docs/chat/summaries/20260603_personal_nameverification_handoff_prompt.md`

## 最初に必ず確認する作業

PR #152 `feat: normalize link management labels` から再開してください。

記録上の状態:

- branch: `feature/link-label-normalization`
- head SHA: `738bf29d7bed0f3fb2e4d6c33965151fcd1aecd4`
- 最新CI: Quality Gates run #196 success
- 直近確認: open / 未merge / CI success / mergeable=false

新チャットでは、この記録を鵜呑みにせず、必ずGitHub上の最新PR/CI状態を再取得してください。

## PR #152 の判断手順

1. PR #152を再取得する。
2. head SHAが変わっていないか確認する。
3. 最新CIがsuccessか確認する。
4. 未解決review指摘がないか確認する。
5. `mergeable=true` ならsquash mergeする。
6. `mergeable=false` / `unknown` / `null` なら、base/head差分、conflict有無、最新CIを再確認する。
7. 必要ならbase追従・競合解消・再CIを行う。
8. merge後、詳細正本の残工程に従って次タスクへ進む。

## 運用方針

- GitHub repoを一次情報として扱う。
- Google Driveは基本参照しない。
- AIがGitHub上で実装、テスト追加、PR作成、CI確認、失敗修正、review対応、mergeまで進める。
- 人間の手元UAT/EXE/portable確認は残工程に入れない。必要時だけ任意確認として扱う。
- 軽いタスクはまとめて進める。
- CI未通過PRはmergeしない。
- merge方式は原則squash merge。
- 毎回「完了済みを除いた残工程一覧」を必ず併記する。

## PR #152 merge後の推奨順

| 優先度 | 残工程 | 難易度 | 内容 |
|---:|---|---:|---|
| P2 | `DELETE-FLOW-CLARITY` | 4 | 削除/復元/完全削除の対象明示・危険操作UI改善 |
| P2 | `USER-MGMT-VISUAL-POLISH` | 4 | ユーザー管理UIの視認性改善 |
| P2 | `TITLE-MGMT-SELECTION-REDESIGN` | 7 | タイトル編集/削除対象を一覧＋検索へ変更 |
| P2 | `SUBTITLE-MGMT-SELECTION-REDESIGN` | 6 | サブタイトル編集/削除対象も一覧＋検索へ変更 |
| P2 | `SHARED-RICH-UI-COMPONENTS` | 6 | 共通カード/summary/toolbar/empty state化 |
| P3 | `AUDIT-DATAIO-HELP-POLISH` | 4 | 監査ログ・データ入出力・ヘルプのUI改善 |

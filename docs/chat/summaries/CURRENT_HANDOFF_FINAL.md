# Personal_NameVerification / 名前解決アプリ 最終引継ぎ入口

作成日: 2026-06-03
対象repo: `kjwork-jp/Personal_NameVerification`

このファイルは、新規チャットへ作業状態を引き継ぐための最終入口です。

## 現在状態

PR #152 から PR #156 までの対応により、詳細正本に記載されていた必須UI改善残工程は完了済みです。

- 最新完了サマリ: `docs/chat/summaries/20260603_personal_nameverification_completion_summary.md`
- 詳細履歴: `docs/chat/summaries/20260603_personal_nameverification_handoff_detail.md`
- 旧入口: `docs/chat/summaries/CURRENT_HANDOFF.md`
- 初回プロンプト履歴: `docs/chat/summaries/20260603_personal_nameverification_handoff_prompt.md`

## 完了済みPR

| PR | 内容 | merge commit |
|---:|---|---|
| #152 | LinkManagementTabの表示名/ID表記正規化 | `253162bc170e296d8a35d97d7e64a4dce4ff8ffa` |
| #153 | 削除データUIとユーザー管理UIの対象明示 | `74c2e10762e6dcd551f51572184d3f504f4de674` |
| #154 | タイトル管理UIの選択対象カード明確化 | `08fabeddee0d1350c9641b9478a3abb54e79b705` |
| #155 | サブタイトル/監査/操作ログ/ヘルプの回帰テスト追加 | `1e2bcca8b1640009a3844769ef293e9ac60325f9` |
| #156 | 共通UI helperの回帰テスト追加 | `4194b1876a35a64574319f0174fb63a4b02fb62b` |

## 完了済み必須残工程

| 残工程 | 状態 |
|---|---|
| `DELETE-FLOW-CLARITY` | 完了 |
| `USER-MGMT-VISUAL-POLISH` | 完了 |
| `TITLE-MGMT-SELECTION-REDESIGN` | 完了 |
| `SUBTITLE-MGMT-SELECTION-REDESIGN` | 完了 |
| `AUDIT-DATAIO-HELP-POLISH` | 完了 |
| `SHARED-RICH-UI-COMPONENTS` | 完了 |

## 現在の残工程

必須残工程はありません。

| 種別 | 残工程 | 人間操作 | 状態 |
|---|---|---|---|
| 任意 | 手元UAT確認 | 任意 | 必須ではない |
| 任意 | 配布物確認 | 任意 | 必須ではない |

## 運用方針

- GitHub repoを一次情報として扱う。
- Google Driveは基本参照しない。
- open PRがある場合は、CI、review thread、mergeableを再確認してから扱う。
- CI未通過PRはmergeしない。
- merge方式は原則squash merge。
- 人間の手元確認は、必要時だけ任意確認として扱う。
- 毎回「完了済みを除いた残工程一覧」を必ず併記する。

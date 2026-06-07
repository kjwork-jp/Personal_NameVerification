# Personal_NameVerification / 名前解決アプリ 最終引継ぎ入口

更新日: 2026-06-07
対象repo: `kjwork-jp/Personal_NameVerification`

このファイルは、新規チャットへ作業状態を引き継ぐための最終入口です。
GitHub repoを一次情報として扱い、Google Driveは基本参照しないでください。

## 現在状態

PR #172 はmerge済みです。現在の最優先は、PR #175 `fix: show trash restore conflicts in UI` のbase/head差分・conflict有無・mergeable再確認です。

- 現行詳細引継ぎ: `docs/chat/summaries/20260607_personal_nameverification_current_handoff.md`
- 旧完了サマリ: `docs/chat/summaries/20260603_personal_nameverification_completion_summary.md`
- 旧詳細履歴: `docs/chat/summaries/20260603_personal_nameverification_handoff_detail.md`
- 旧入口: `docs/chat/summaries/CURRENT_HANDOFF.md`
- 初回プロンプト履歴: `docs/chat/summaries/20260603_personal_nameverification_handoff_prompt.md`

## 最初に確認するPR

| 項目 | 内容 |
|---|---|
| PR | #175 |
| Title | `fix: show trash restore conflicts in UI` |
| Branch | `feature/trash-restore-conflict-feedback` |
| Base | `main` |
| Head SHA | `b32dd6010a7acf3761f7ada658390c3ac12c1636` |
| 最新CI | Quality Gates #247 success |
| 直近確認 | open / 未merge / CI success / mergeable=false |

新チャットの最初の実作業:

1. PR #175 の最新状態を再取得する。
2. head SHA、CI success、review未解決指摘、mergeable状態を確認する。
3. 直近ではhandoff docs更新commitでmainが進んだ後に `mergeable=false` を確認しているため、base/head差分とconflict有無を確認する。
4. 実conflictがなければbase追従またはGitHub再評価後、必要なら再CIを行う。
5. `mergeable=true` かつ Quality Gates success になったらPR #175をsquash mergeする。
6. merge後、現行詳細引継ぎの残工程へ進む。

注意:

- `mergeable=false` / `unknown` / `null` の場合、GitHub側の一時評価遅延、base branch更新、または実競合の可能性がある。
- その場合はPRを再取得し、base/head差分・conflict有無・最新CIを確認する。
- 必要ならbase追従・競合解消commitを作成し、再CI通過後にmergeする。

## 完了済みPR

| PR | 内容 | merge commit |
|---:|---|---|
| #152 | LinkManagementTabの表示名/ID表記正規化 | `253162bc170e296d8a35d97d7e64a4dce4ff8ffa` |
| #153 | 削除データUIとユーザー管理UIの対象明示 | `74c2e10762e6dcd551f51572184d3f504f4de674` |
| #154 | タイトル管理UIの選択対象カード明確化 | `08fabeddee0d1350c9641b9478a3abb54e79b705` |
| #155 | サブタイトル/監査/操作ログ/ヘルプの回帰テスト追加 | `1e2bcca8b1640009a3844769ef293e9ac60325f9` |
| #156 | 共通UI helperの回帰テスト追加 | `4194b1876a35a64574319f0174fb63a4b02fb62b` |
| #172 | title/subtitle表示名重複のservice validation | `be85d00f993aa17995fac3f489ab5fe95b172444` |

## 現在の残工程

詳細は `docs/chat/summaries/20260607_personal_nameverification_current_handoff.md` を正本として扱ってください。

| 優先度 | 残工程 | 人間操作 | 状態 |
|---:|---|---|---|
| P0 | PR #175 base/head差分・conflict有無・mergeable再確認 | 不要 | CI success / 直近mergeable=false。handoff docs更新後のbase進行影響を確認 |
| P0 | PR #175 必要ならbase追従・再CI・squash merge | 不要 | mergeable回復後 |
| P0 | UI事前チェックで重複入力を登録前に止める | 不要 | #175 merge後 |
| P0 | Issue #174: import経路のtitle/subtitle重複validation | 不要 | 起票済み / 未着手 |
| P0 | DB制約化前のpreflight/cleanup設計 | 不要 | DB制約化の前提 |
| P0 | 日時表示統一の残画面適用 | 不要 | 残画面確認が必要 |
| P0 | 一覧カラム削減 + 詳細ペイン化 | 不要 | 仕様docs済み / 未着手 |
| P0 | タイトル編集画面のUI崩れ修正 | 不要 | 未着手 |
| P0 | サブタイトル編集をサブタイトル起点へ再設計 | 不要 | 未着手 |
| P0 | 監査ログ差分表示改善 | 不要 | 未着手 |

## Secret / Settings方針

追加登録が必要なSecretはありません。

- `Contents write / Pull requests write / Issues write / Actions read/write` は設定済み前提。
- このrepoは長期継続保守・外部secret運用タイプではないため、1Passwordは不要。
- `OP_SERVICE_ACCOUNT_TOKEN` は不要。
- `PERSONAL_NAMEVERIFICATION_BOT_TOKEN` は不要。

## 運用方針

- GitHub repoを一次情報として扱う。
- Google Driveは基本参照しない。
- open PRがある場合は、CI、review thread、mergeableを再確認してから扱う。
- CI未通過PRはmergeしない。
- merge方式は原則squash merge。
- 人間の手元確認は、必要時だけ任意確認として扱う。
- 毎回「完了済みを除いた残工程一覧」を必ず併記する。

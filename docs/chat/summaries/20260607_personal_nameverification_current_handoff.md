# Personal_NameVerification / 名前解決アプリ 現行引継ぎ詳細 2026-06-07

対象repo: `kjwork-jp/Personal_NameVerification`

このファイルは、新規チャットへ現行作業状態を引き継ぐための詳細版です。GitHub repoを一次情報として扱い、チャット本文やローカル手元メモより、このファイル、PR、Issue、CI状態を優先してください。

---

## 1. 最重要の現在地点

### まず確認するPR

- PR: #175
- Title: `fix: show trash restore conflicts in UI`
- Branch: `feature/trash-restore-conflict-feedback`
- Base: `main`
- Head SHA: `b32dd6010a7acf3761f7ada658390c3ac12c1636`
- State: open
- Merged: false
- 直近再確認: `mergeable=false`
- 最新CI: Quality Gates #247 success
- CI内訳: ruff / black / mypy / pytest success

### 新規チャットの最初の実作業

1. PR #175 の最新状態を再取得する。
2. head SHA が `b32dd6010a7acf3761f7ada658390c3ac12c1636` 以降であることを確認する。
3. Quality Gates がsuccessであることを確認する。
4. review thread未解決がないことを確認する。
5. `mergeable=false` の原因を確認する。
6. 今回はhandoff docs更新commitでmainが進んだ直後に `mergeable=false` へ変わったため、まずbase/head差分とconflict有無を確認する。
7. 実conflictがなければbase追従commitまたはGitHub側の再評価を待って、必要なら再CIを通す。
8. `mergeable=true` かつ Quality Gates success になったら、PR #175をsquash mergeする。
9. merge後、次P0へ進む。

注意:

- CI未通過PRはmergeしない。
- `mergeable=false` / `unknown` / `null` の場合は、base/head差分、conflict有無、最新CIを再確認し、必要ならbase追従・競合解消・再CIを行う。
- merge方式は原則squash merge。

---

## 2. 直近で完了した主要作業

### PR #172: duplicate display-name service validation

- PR: #172
- Title: `feat: validate duplicate display names in service`
- State: merged
- Merge commit: `be85d00f993aa17995fac3f489ab5fe95b172444`
- 最終CI: Quality Gates #244 success
- 内容:
  - title/subtitle create/update/restoreで、プロジェクト正規化ベースの重複表示名validationを追加。
  - DB unique indexは追加しない。
  - `BEGIN IMMEDIATE` によるwrite transaction直列化を追加。
  - legacy blank rowsはscan時に非ブロック。
  - legacy duplicate環境では、表示名を変えないmetadata editを許可。

### Issue #174: import経路validation

- Issue: #174
- Title: `Validate duplicate title/subtitle display names in import paths`
- State: open
- 背景:
  - PR #172のreview中に、CSV/JSON import経路の重複validationは範囲が広いため後続分離した。
- Scope:
  - ImportService / CSV / JSON import経路を確認。
  - CoreServiceと同じ正規化ルールで、active title名と同一title配下subtitle名の重複を拒否。
  - import payload内重複と既存DB active行との衝突を検出。
  - DB unique index追加は非目標。

### PR #175: restore conflict UI feedback

- PR: #175
- State: open / merge待ち
- Head SHA: `b32dd6010a7acf3761f7ada658390c3ac12c1636`
- Quality Gates #247: success
- 直近再確認: `mergeable=false`
- 推定原因: handoff docs更新でmainが進んだため。実conflict有無は新チャットで再確認する。
- 内容:
  - `TrashTab._restore_selected()` で `ConflictError`, `StateTransitionError`, `ValidationError` を捕捉。
  - raw service exceptionを漏らさず、`message_label` に「復元できません: ...」を表示。
  - 失敗時は `_reload()` 後にエラーメッセージを再表示し、通常の一覧取得メッセージで上書きしない。
  - `tests/test_trash_tab_ui.py` に復元ConflictErrorのUI回帰テストを追加。

---

## 3. 基本運用方針

- GitHub repoを一次情報として扱う。
- Google Driveは基本参照しない。
- AIがGitHub上で、実装・テスト追加・PR作成・CI確認・失敗修正・review対応・mergeまで進める。
- 人間の手元UAT/EXE/portable確認は残工程に入れない。
- 手元確認は、ユーザーがやりたい時だけ任意確認として扱う。
- 軽いタスクは小分けにせず、まとめて進める。
- 毎回、必ず「完了済みを除いた残工程一覧」を併記する。
- 残工程表は「優先度 / 残工程 / 難易度 / 人間操作 / 状態」を基本列にする。
- 完了済みタスクは残工程一覧から除外する。
- CI未通過PRはmergeしない。
- GitHub review / Codex review指摘が妥当ならmerge前に対応する。
- merge方式は原則squash merge。
- コマンドが必要な場合は、PowerShell前提で完全コマンドを書く。

ユーザーに確認を求めるのは、以下の場合だけ:

- GitHub権限不足で操作できない。
- 破壊的操作や設定変更が必要で、影響範囲が不明。
- CI/PR状態が矛盾していて、複数の復旧方針が同程度に妥当。
- 手元環境でしか確認できない問題が発生した。

それ以外はGitHub上で自律的に進める。

---

## 4. Secret / Settings方針

現時点で追加登録が必要なSecretはない。

- `Contents write / Pull requests write / Issues write / Actions read/write` は設定済み前提。
- このrepoは長期継続保守・外部secret運用タイプではないため、1Passwordは不要。
- `OP_SERVICE_ACCOUNT_TOKEN` は不要。
- `PERSONAL_NAMEVERIFICATION_BOT_TOKEN` は不要。
- Codex review creditは任意。開発継続の必須条件ではない。

---

## 5. 完了済みを除いた残工程一覧

| 優先度 | 残工程 | 難易度 | 人間操作 | 状態 |
|---:|---|---:|---|---|
| P0 | PR #175 base/head差分・conflict有無・mergeable再確認 | 3 | 不要 | CI success / 直近mergeable=false。handoff docs更新後のbase進行影響を確認 |
| P0 | PR #175 必要ならbase追従・再CI・squash merge | 4 | 不要 | mergeable回復後 |
| P0 | UI事前チェックで重複入力を登録前に止める | 6 | 不要 | #175 merge後 |
| P0 | Issue #174: import経路のtitle/subtitle重複validation | 7 | 不要 | 起票済み / 未着手 |
| P0 | DB制約化前のpreflight/cleanup設計 | 7 | 不要 | DB制約化の前提。PR #172ではDB制約追加なし |
| P0 | 日時表示統一の残画面適用 | 5 | 不要 | 削除データ/監査ログは完了。残画面確認が必要 |
| P0 | 一覧カラム削減 + 詳細ペイン化 | 8 | 不要 | 仕様docs済み / 未着手 |
| P0 | タイトル編集画面のUI崩れ修正 | 6 | 不要 | 未着手 |
| P0 | サブタイトル編集をサブタイトル起点へ再設計 | 8 | 不要 | 未着手 |
| P0 | 監査ログ差分表示改善 | 7 | 不要 | 未着手 |
| P1 | タイトル一覧に名前絞り込み追加 | 5 | 不要 | 未着手 |
| P1 | 関連付け解除粒度改善 | 6 | 不要 | 未着手 |
| P1 | 検索画面の単一表 + 詳細ペイン化 | 8 | 不要 | 未着手 |
| P1 | Data I/O 文言改善・日本語化 | 5 | 不要 | 未着手 |

---

## 6. 新規チャット用プロンプト

以下を新規チャットに貼る。

```md
GitHub repo `kjwork-jp/Personal_NameVerification` の名前解決アプリ開発を継続してください。

まずGitHub上の以下の最終引継ぎ入口Markdownを一次情報として読んでください。

- `docs/chat/summaries/CURRENT_HANDOFF_FINAL.md`

そのうえで、同ファイルが参照している現行詳細引継ぎMarkdownも確認してください。

重要方針:

- GitHub repoを一次情報として扱う。
- Google Driveは基本参照しない。
- AIがGitHub上で実装、テスト追加、PR作成、CI確認、失敗修正、review対応、mergeまで進める。
- 人間の手元UAT/EXE/portable確認は残工程に入れない。必要時だけ任意確認として扱う。
- 軽いタスクはまとめて進める。
- 毎回「完了済みを除いた残工程一覧」を必ず併記する。
- CI未通過PRはmergeしない。
- merge方式は原則squash merge。
- `Contents write / Pull requests write / Issues write / Actions read/write` は設定済み前提。
- このrepoでは1Password/OP_SERVICE_ACCOUNT_TOKENは不要。

最初にやること:

1. PR #175 `fix: show trash restore conflicts in UI` の最新状態を確認する。
2. head SHA、CI success、review未解決指摘、mergeable状態を確認する。
3. 現時点ではhandoff docs更新でmainが進んだ後に `mergeable=false` を確認しているため、まずbase/head差分とconflict有無を確認する。
4. 実conflictがなければbase追従またはGitHub再評価後、必要なら再CIを行う。
5. `mergeable=true` かつ Quality Gates success ならPR #175をsquash mergeする。
6. merge後、詳細引継ぎMarkdownの残工程に従って次タスクへ進む。

現時点の記録:

- PR #175 branch: `feature/trash-restore-conflict-feedback`
- head SHA: `b32dd6010a7acf3761f7ada658390c3ac12c1636`
- 最新CI: Quality Gates run #247 success
- 直近確認: open / 未merge / CI success / mergeable=false
- 推定原因: handoff docs更新commitでmainが進んだため。実conflict有無は再確認すること。

回答では、要点サマリ、今回実施した作業、現在状態、完了済みを除いた残工程一覧を出してください。
```

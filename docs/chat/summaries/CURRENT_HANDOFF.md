# Personal_NameVerification / 名前解決アプリ 現行引継ぎ入口

このファイルは、新規チャットへ作業を引き継ぐための**安定参照先**です。
詳細版や日付付き履歴が増えても、新チャットではまずこのファイルを確認してください。

作成日: 2026-06-03
対象repo: `kjwork-jp/Personal_NameVerification`

---

## 1. 参照すべき正本

現行の詳細引継ぎ正本:

- `docs/chat/summaries/20260603_personal_nameverification_handoff_detail.md`

新チャット初回貼り付け用プロンプト:

- `docs/chat/summaries/20260603_personal_nameverification_handoff_prompt.md`

この `CURRENT_HANDOFF.md` は入口です。詳細は上記2ファイルを参照してください。

---

## 2. 新チャットで最初に貼るプロンプト

```markdown
GitHub repo `kjwork-jp/Personal_NameVerification` の名前解決アプリ開発を継続してください。

まずGitHub上の以下の現行引継ぎ入口Markdownを一次情報として読んでください。

- `docs/chat/summaries/CURRENT_HANDOFF.md`

そのうえで、CURRENT_HANDOFF.md が参照している詳細引継ぎMarkdownも確認してください。

重要方針:

- GitHub repoを一次情報として扱う。
- Google Driveは基本参照しない。
- AIがGitHub上で実装、テスト追加、PR作成、CI確認、失敗修正、review対応、mergeまで進める。
- 人間の手元UAT/EXE/portable確認は残工程に入れない。必要時だけ任意確認として扱う。
- 軽いタスクはまとめて進める。
- 毎回「完了済みを除いた残工程一覧」を必ず併記する。
- CI未通過PRはmergeしない。
- merge方式は原則squash merge。

最初にやること:

1. PR #152 `feat: normalize link management labels` の最新状態を確認する。
2. head SHA、CI success、review未解決指摘、mergeable状態を確認する。
3. 問題なければPR #152をsquash mergeする。
4. merge後、詳細引継ぎMarkdownの残工程に従って次タスクへ進む。

現時点の記録:

- PR #152 branch: `feature/link-label-normalization`
- head SHA: `738bf29d7bed0f3fb2e4d6c33965151fcd1aecd4`
- 最新CI: Quality Gates run #196 success
- 直近確認: open / 未merge / mergeable=true

回答では、要点サマリ、今回実施した作業、現在状態、完了済みを除いた残工程一覧を出してください。
```

---

## 3. 最初の実作業

最初にやることは、PR #152 の最新状態確認とmergeです。

1. PR #152を再取得する。
2. 最新head SHAが `738bf29d7bed0f3fb2e4d6c33965151fcd1aecd4` から変わっていないか確認する。
3. 最新CIがsuccessか確認する。
4. 未解決review指摘がないか確認する。
5. `mergeable=true` ならsquash mergeする。
6. merge後、次の残工程へ進む。

`mergeable=false` や `unknown/null` の場合は、GitHub側の一時評価遅延、base branch更新、または実競合の可能性があります。再取得、base/head差分、conflict有無、最新CIを確認してください。

---

## 4. 現行の残工程

PR #152 merge後の推奨順:

| 優先度 | 残工程 | 難易度 | 内容 |
|---:|---|---:|---|
| P2 | `DELETE-FLOW-CLARITY` | 4 | 削除/復元/完全削除の対象明示・危険操作UI改善 |
| P2 | `USER-MGMT-VISUAL-POLISH` | 4 | ユーザー管理UIの視認性改善 |
| P2 | `TITLE-MGMT-SELECTION-REDESIGN` | 7 | タイトル編集/削除対象をドロップダウンから一覧＋検索へ変更 |
| P2 | `SUBTITLE-MGMT-SELECTION-REDESIGN` | 6 | サブタイトル編集/削除対象も一覧＋検索へ変更 |
| P2 | `SHARED-RICH-UI-COMPONENTS` | 6 | 共通カード/summary/toolbar/empty state化 |
| P3 | `AUDIT-DATAIO-HELP-POLISH` | 4 | 監査ログ・データ入出力・ヘルプのUI磨き込み |

---

## 5. 注意事項

- このファイルの内容よりも、GitHub上の最新PR/CI状態を優先してください。
- PR #152が既にmerge済みの場合は、詳細引継ぎMarkdownの残工程から再開してください。
- 手元UAT/EXE/portable確認は残工程に入れないでください。
- Google Driveは基本参照しないでください。
- CI失敗時は最新head commitのrunを確認してください。古いrunで判断しないでください。

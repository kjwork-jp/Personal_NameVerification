# Personal_NameVerification / 名前解決アプリ 新チャット初回プロンプト

このファイルは、新規チャット冒頭に貼る短縮プロンプトです。
詳細は同ディレクトリの `20260603_personal_nameverification_handoff_detail.md` を参照してください。

---

## 貼り付け用プロンプト

```markdown
GitHub repo `kjwork-jp/Personal_NameVerification` の名前解決アプリ開発を継続してください。

まずGitHub上の以下の引継ぎ詳細Markdownを一次情報として読んでください。

- `docs/chat/summaries/20260603_personal_nameverification_handoff_detail.md`

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
4. merge後、引継ぎ詳細Markdownの残工程に従って次タスクへ進む。

現時点の記録:

- PR #152 branch: `feature/link-label-normalization`
- head SHA: `738bf29d7bed0f3fb2e4d6c33965151fcd1aecd4`
- 最新CI: Quality Gates run #196 success
- 直近確認: open / 未merge / mergeable=true

回答では、要点サマリ、今回実施した作業、現在状態、完了済みを除いた残工程一覧を出してください。
```

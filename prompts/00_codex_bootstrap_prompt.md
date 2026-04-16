# 00_codex_bootstrap_prompt.md

あなたは **NameVerification v3** の実装担当です。
このリポジトリは **空の状態から完全再構築** する前提であり、既存実装の踏襲ではなく、**文書を正本とした再実装** を行います。

このプロンプトは、Codex が最初に読むべき実行指示です。  
曖昧な補完や過剰な善意は不要です。**正確さ・設計整合・レビュー容易性** を優先してください。

---

## 0. 目的
以下を満たす Python デスクトップアプリを、段階的な PR 方式で構築してください。

- Windows 11 ローカル実行
- GUI は **PySide6 のみ**
- Python 3.12 系
- SQLite を単一正本 DB とする
- PyInstaller による exe 化を前提とする
- 検索/照合、CRUD、ゴミ箱、移行、監査、運用導線を含む

---

## 1. 最初に読む順番
以下を **必ずこの順番で** 読んでください。

1. `docs/02_document_priority_order.md`
2. `docs/00_repository_master_spec.md`
3. `docs/01_role_responsibility_matrix.md`
4. `docs/10_requirements_definition.md`
5. `docs/11_acceptance_criteria.md`
6. `docs/12_basic_design.md`
7. `docs/13_detailed_technical_design.md`
8. `docs/14_ui_ux_design.md`
9. `docs/15_data_design.md`
10. `docs/16_error_handling_policy.md`
11. `docs/18_search_behavior_spec.md`
12. `docs/19_permissions_rbac_spec.md`
13. `docs/20_icon_file_handling_spec.md`
14. `docs/30_development_process_map.md`
15. `docs/31_branch_and_pr_policy.md`
16. `docs/32_coding_rules.md`
17. `docs/33_directory_structure_policy.md`
18. `docs/34_definition_of_done.md`
19. `docs/35_definition_of_ready.md`
20. `docs/39_dependency_policy.md`
21. `docs/40_test_strategy.md`
22. `docs/41_test_level_matrix.md`
23. `docs/43_review_checklist.md`
24. `docs/44_final_review_checklist.md`
25. `docs/50_operations_design.md`
26. `docs/51_backup_restore_policy.md`
27. `docs/52_logging_audit_policy.md`
28. `docs/53_release_and_deployment_policy.md`
29. `docs/54_go_live_checklist.md`
30. `prompts/01_codex_work_rules.md`
31. `prompts/02_codex_pr_template.md`
32. `prompts/03_codex_task_split_examples.md`
33. `prompts/04_codex_no_assumption_rules.md`

**読了後、最初にやることは実装ではなく、作業計画の明文化です。**

---

## 2. あなたの担当範囲
あなたの担当は以下です。

- リポジトリ初期ブートストラップ
- ディレクトリ作成
- アプリ本体の実装
- 単体テスト
- 初期結合テスト
- 必要最小限の補助スクリプト作成
- PR 作成
- セルフレビュー

担当外:

- 要件の再定義
- 設計方針の独断変更
- 運用開始可否の最終判定
- UAT の最終承認
- docs の意味を変えるような仕様変更

---

## 3. 絶対にしてはいけないこと
以下は禁止です。

- `main` へ直接 push
- 1 PR に複数目的を混在
- 未承認の設計追加
- 文書根拠なしの依存追加
- Tkinter の再導入、併存、名称残し
- UI 層から SQL を直接実行
- 一時しのぎの命名（`temp`, `final2`, `poc`, `new_new` など）
- テストなしの重要機能追加
- 破壊的変更を PR 本文で明示しないこと

---

## 4. 不明点がある場合の扱い
不明点がある場合は、勝手に決めず、以下の順で処理してください。

1. `docs/02_document_priority_order.md` に従って上位文書を再確認
2. `docs/97_open_issues_and_constraints.md` を確認
3. それでも未確定なら、実装に埋め込まず backlog 化
4. PR 本文の「未対応」に記載

**補完実装より、未確定の明示を優先してください。**

---

## 5. 実装の基本方針
以下の原則で進めてください。

- 1タスク 1ブランチ
- 1ブランチ 1PR
- 小さい差分で積み上げる
- docs を根拠にコードを書く
- コード変更に追随するテストを書く
- 重要な変更には再発防止テストを付ける
- 破壊的変更時は docs 更新をセットにする

優先順位:

1. 正確さ
2. 文書整合
3. 保守性
4. テスト容易性
5. 実装速度

---

## 6. 最初の実行手順
最初のセッションでは、以下の順で進めてください。

### Step 1: 読了確認
- 上記文書を読む
- 実装対象・非対象・制約を整理する

### Step 2: 初回作業計画
以下を箇条書きで出力する。
- 今回の PR の目的
- 対象ファイル
- 影響範囲
- 実行予定テスト
- 未着手に残すもの

### Step 3: 最初の PR スコープ
最初の PR は、可能なら以下のいずれかの粒度にする。
- `chore/bootstrap-python-project`
- `feature/define-sqlite-schema`
- `feature/implement-normalization-rules`
- `feature/implement-name-service`
- `feature/implement-pyside6-main-entrypoint`

**初回から全部実装しないでください。**

### Step 4: 変更実施
- ディレクトリ作成
- 必要ファイル追加
- 実装
- テスト追加

### Step 5: 自己確認
- lint / format / type / test を可能な範囲で実施
- docs 整合を確認

### Step 6: PR 作成
- `prompts/02_codex_pr_template.md` に沿って PR を作成
- 仕様根拠に参照文書を明記
- 未確定事項・未対応事項を明示

---

## 7. 初回ブートストラップで期待する最低成果
初回～初期数 PR で最低限ほしいもの:

- Python プロジェクトの土台
- 推奨ディレクトリ構造
- `app/pyside6_main.py` の正式起動点
- `db/schema.sql`
- 基本 logging 基盤
- domain/application/infrastructure の最小骨格
- pytest 実行環境
- ruff / black / mypy 設定
- PyInstaller の雛形

---

## 8. テスト要件
最低限、変更に応じて以下を実施してください。

- domain: 単体テスト
- application: 単体または結合テスト
- import/export/backup/restore: 結合テスト優先
- 権限制御: viewer/editor/admin 境界を確認
- 削除/復元/完全削除: 状態遷移テスト必須

テストを省略した場合は、理由を PR に明記してください。

---

## 9. ブランチ・PR 規約
- ブランチ命名は `docs/31_branch_and_pr_policy.md` に従う
- PR タイトルは `type: summary`
- PR 本文は `prompts/02_codex_pr_template.md` を使う
- 仕様根拠として参照した docs を列挙する

---

## 10. 依存ライブラリのルール
許容前提:
- PySide6
- pytest / pytest-cov
- ruff
- black
- mypy
- PyInstaller

追加したい場合:
- `docs/39_dependency_policy.md` を確認
- 追加理由、代替不可理由、影響範囲を PR に書く
- 勝手に大型依存を増やさない

---

## 11. UI 実装ルール
- GUI は PySide6 のみ
- 検索/照合が主導線
- CRUD と参照を混在させすぎない
- destructive 操作には確認ダイアログ
- status 表示と error 表示を分離
- UI は use case を経由して機能実行する

---

## 12. DoR / DoD
着手前:
- `docs/35_definition_of_ready.md` を満たすこと

完了条件:
- `docs/34_definition_of_done.md` を満たすこと
- テスト結果があること
- PR 本文が埋まっていること
- セルフレビューがあること
- 最終的に `docs/44_final_review_checklist.md` に照らして問題がないこと

---

## 13. 最後に出力すべき内容
各作業の最後に必ず以下を出力してください。

1. 今回の目的
2. 変更ファイル一覧
3. 実施テストと結果
4. 仕様根拠
5. 残課題
6. 次 PR の推奨スコープ

---

## 14. 最初の一文で宣言すること
作業開始時、最初に次を宣言してください。

> 文書優先順位・要件定義・設計文書を確認し、今回の PR では 1目的に限定して実装します。未確定事項は推測せず backlog 化します。

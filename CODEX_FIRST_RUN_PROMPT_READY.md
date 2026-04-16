# 05_codex_first_execution_prompt_complete.md

以下を **Codex の最初の指示文** として、そのまま貼り付けて使用する。

---

あなたは **NameVerification v3** リポジトリの実装担当です。  
このリポジトリは空の状態から完全再構築します。既存コードの踏襲ではなく、**リポジトリ内文書を唯一の正本** として実装してください。

最初に、以下の順番で文書を読んでください。

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
34. `prompts/00_codex_bootstrap_prompt.md`

読了後、いきなり実装を始めず、以下を最初に出力してください。

- 今回の PR の目的
- 今回の PR で扱う範囲 / 扱わない範囲
- 変更予定ファイル
- 参照した仕様根拠ファイル
- 実施予定テスト
- 残す未対応事項

制約:
- main へ直接 push 禁止
- 1 PR 1目的
- Tkinter の再導入禁止
- 文書根拠なしの依存追加禁止
- 不明点の推測実装禁止
- UI 層から SQL 直接実行禁止

技術前提:
- Python 3.12
- PySide6
- SQLite
- pytest / pytest-cov
- ruff / black / mypy
- PyInstaller

最初の PR 候補は、以下のような小さい粒度から選んでください。

- `chore/bootstrap-python-project`
- `feature/define-sqlite-schema`
- `feature/implement-normalization-rules`
- `feature/implement-name-service`
- `feature/implement-pyside6-main-entrypoint`

今回の実装では、**一度に全部作らず、小さい PR に分けてください。**

各 PR の最後には必ず以下を出力してください。

1. 目的
2. 変更ファイル一覧
3. テスト結果
4. 仕様根拠
5. リスク
6. 未対応
7. 次 PR の推奨スコープ

また、作業開始時の最初の一文として次を宣言してください。

> 文書優先順位・要件定義・設計文書を確認し、今回の PR では 1目的に限定して実装します。未確定事項は推測せず backlog 化します。

---

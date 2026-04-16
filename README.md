# NameVerification v3 Repository Bootstrap Package

## 概要
本リポジトリは、**Windows ローカル環境で動作する名前照合・登録デスクトップアプリ**を、PySide6 前提でゼロから再構築するための設計・運用・AI連携ドキュメント一式です。

現時点では**コードは含みません**。  
このパッケージは、以下の役割分担を前提にした**実装前の完全な土台**です。

- 要件定義～設計: ChatGPT
- 開発～テスト初期: Codex
- テスト後期～運用開始前: ChatGPT

## 目的
- 実装前に、要件・設計・開発工程・品質基準・運用基準を固定する
- AI 実装時の解釈ブレを抑える
- Git / PR / テスト / 運用開始判定までを一貫して管理する

## 想定プロダクト
- 名称: NameVerification v3
- 方式: Windows デスクトップアプリ
- UI: PySide6
- DB: SQLite
- 配布形態: PyInstaller による exe 配布
- 利用形態: 原則オフライン、単一拠点ローカル運用

## まず読む順番
1. `docs/02_document_priority_order.md`
2. `docs/00_repository_master_spec.md`
3. `docs/10_requirements_definition.md`
4. `docs/12_basic_design.md`
5. `docs/13_detailed_technical_design.md`
6. `docs/31_branch_and_pr_policy.md`
7. `docs/40_test_strategy.md`
8. `docs/50_operations_design.md`
9. `prompts/01_codex_work_rules.md`
10. `prompts/00_codex_bootstrap_prompt.md`

## このパッケージに含むもの
- リポジトリ設計書
- 役割表
- 要件定義書
- 基本設計 / 技術詳細設計書
- 運用設計書
- 開発工程マップ
- Codex 用プロンプト群
- ブランチ / PR 運用規約
- テスト / UAT / リリース判定基準

## 実装開始時の大原則
- main へ直接 push しない
- 1 PR 1目的
- 推測で仕様を補わない
- 設計変更時は docs を先に更新する
- 各工程末尾に**徹底的な最終見直しレビュー**を行う

## オーナー
- Repository owner: `kjwork-jp`

## 版管理
- Bootstrap package version: `v3-bootstrap-2026-04-15`

## ライセンス
本パッケージの既定ライセンスは `LICENSE` を参照してください。

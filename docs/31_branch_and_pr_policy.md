# 31_branch_and_pr_policy.md

## 1. 基本ルール
- main へ直接 push 禁止
- 必ず branch + PR 経由
- 1 PR 1目的
- 仕様変更を含む場合は docs 更新必須

## 2. ブランチ命名
- `docs/<topic>`
- `feature/<topic>`
- `fix/<topic>`
- `refactor/<topic>`
- `test/<topic>`
- `chore/<topic>`

### 例
- `docs/bootstrap-governance`
- `feature/pyside6-main-window`
- `feature/search-usecase`
- `fix/rbac-delete-guard`
- `test/search-filter-regression`

## 3. PR 単位
適正サイズの目安:
- 変更行数はレビュー可能な粒度
- 目的が 1 つに説明できる
- UI と DB の大変更は可能なら分割

## 4. PR タイトル規則
- `docs: ...`
- `feature: ...`
- `fix: ...`
- `refactor: ...`
- `test: ...`

## 5. PR 本文必須項目
- 目的
- 背景
- 仕様根拠
- 変更内容
- テスト
- リスク
- 未対応
- レビュー観点

## 6. マージ条件
- [ ] テスト通過
- [ ] docs 更新済み
- [ ] セルフレビュー済み
- [ ] 最終レビュー観点確認済み
- [ ] Human Owner 承認済み

## 7. 禁止事項
- WIP のまま main へ混ぜる
- unrelated 変更の抱き合わせ
- レビュー指摘未反映で自己判断マージ

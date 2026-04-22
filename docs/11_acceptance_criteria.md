# 11_acceptance_criteria.md

## 1. 目的
本書は、NameVerification v3 の受入可否を判断するための条件を定義する。

## 2. 受入条件
### 2.1 機能
- [ ] 名前検索が成立する
- [ ] 完全一致 / 部分一致が区別される
- [ ] タイトル / サブタイトル CRUD が成立する
- [ ] 名前とサブタイトルの関連付けが成立する
- [ ] 論理削除 / 復元 / 完全削除が区別される
- [ ] CSV / JSON Export / Import が成立する
- [ ] バックアップ / 復旧が成立する
- [ ] 監査ログが記録される
- [ ] CSV / JSON / SQL dump export が editor/admin で成立する
- [ ] backup create が editor/admin で成立する
- [ ] backup restore が admin で成立する（viewer/editor は拒否される）
- [ ] CSV / JSON import が空DBに対して admin で成立する（viewer/editor は拒否される）
- [ ] 非空DBへの import は拒否される

### 2.2 権限（read / write / destructive 分離）
#### viewer
- [ ] 検索、詳細参照、タイトル/サブタイトル一覧参照、既存リンク参照ができる
- [ ] ゴミ箱/削除済み一覧と監査ログを閲覧できる
- [ ] 作成/更新/リンク操作（write）ができない
- [ ] 論理削除/復元/完全削除（destructive）ができない

#### editor
- [ ] viewer の read-only 操作をすべて実行できる
- [ ] 作成/更新/リンク操作（write）を実行できる
- [ ] 論理削除/復元/完全削除（destructive）ができない

#### admin
- [ ] read-only / write / destructive を実行できる
- [ ] ゴミ箱表示対象に対して復元/完全削除を実行できる

### 2.3 UI
- [ ] 検索主導線が明確
- [ ] destructive 操作に確認ダイアログがある
- [ ] エラー表示が利用者に理解可能
- [ ] 主要操作がキーボードでも到達可能

### 2.4 品質
- [ ] 単体テストが通る
- [ ] 主要結合シナリオが通る
- [ ] UAT シナリオが通る
- [ ] ドキュメント更新漏れがない

### 2.5 運用
- [ ] バックアップ手順が実行可能
- [ ] 復旧手順が実行可能
- [ ] ログ保存先が明示されている
- [ ] 運用開始前チェックリストが埋められる

## 3. 不合格条件
- 主要シナリオが未実装
- 監査ログが残らない
- 文書と実装が一致しない
- Tkinter 前提が残る
- 復旧手順が未検証
- RBAC において read / write / destructive の区分が曖昧

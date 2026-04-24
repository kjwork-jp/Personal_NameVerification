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
- [ ] Operations タブから export / import / backup / restore 導線に到達できる
- [ ] viewer は Operations 操作ボタンが無効、editor は export/backup create のみ有効、admin は全操作有効
- [ ] restore / import 実行前に確認ダイアログが表示される
- [ ] Operations タブの Browse ボタンで native file/directory dialog が開く
- [ ] 入力欄ごとに recent path history（最大5件）が復元・候補表示される
- [ ] Operations 実行結果（success/error/cancel）がローカル JSONL に追記保存される
- [ ] Operations 実行中は busy 表示と二重起動防止が働き、cancel request 導線が利用できる
- [ ] Operations ログの rotation / TTL pruning が動作する
- [ ] recent path history を一括クリアできる
- [ ] Operations 実行ログの最新N件をアプリ内で再読込・閲覧できる
- [ ] log viewer で archive 含有切替 / status-action filter / message 検索ができる
- [ ] log viewer の message 検索で regex モードを切替できる（無効 regex はエラー表示のみでUI継続）
- [ ] log viewer の表示順を 最新順 / 古い順 で切替できる
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

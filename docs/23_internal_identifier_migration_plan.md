# 内部ID / UUID移行設計

## 目的

利用者がIDやコードを手入力しない業務アプリへ移行する。画面上は名前・タイトル名・サブタイトル名を中心に操作し、内部識別子はアプリが自動管理する。

## 現状

- 主要テーブルは整数IDを主キーとして持つ。
- 画面やテストの一部に内部ID・コードの概念が残っている。
- サブタイトル管理番号は未入力時に自動生成されるようになったが、既存互換のため入力欄自体は残っている。
- 操作者は起動時に自動入力されるが、明示変更は可能。

## 移行方針

### 基本方針

- 既存の整数IDは当面DB内部主キーとして維持する。
- 利用者に見せる識別子として `public_id` を追加する。
- `public_id` は UUID 文字列を基本とする。
- UI・CSV/JSON出力・将来の外部連携では `public_id` を使う。
- DB内部のJOINや既存テスト互換は整数IDで維持する。

## 対象テーブル

優先対象は以下。

| テーブル | 現行ID | 追加予定 | 用途 |
|---|---|---|---|
| names | id | public_id | 名前の外部表示用ID |
| titles | id | public_id | タイトルの外部表示用ID |
| subtitles | id | public_id | サブタイトルの外部表示用ID |
| name_subtitle_links | id | public_id | 関連付けの外部表示用ID |
| name_title_links | id | public_id | 名前とタイトルの関連付け外部表示用ID |
| change_logs | id | public_id | 操作履歴の外部表示用ID |

## 推奨スキーマ変更

各テーブルに次を追加する。

```sql
public_id TEXT NOT NULL UNIQUE
```

SQLiteでは既存行に対する `NOT NULL` 追加が扱いにくいため、migrationでは以下の順序にする。

1. nullableな `public_id` を追加する。
2. 既存行へ UUID を埋める。
3. unique index を作る。
4. 新規作成時はアプリ側で必ず UUID を生成する。

## UUID生成方針

- Python標準の `uuid.uuid4()` を使う。
- DB default に依存しない。
- application層またはinfrastructure層の保存直前で生成する。
- 形式は標準UUID文字列にする。

例:

```text
550e8400-e29b-41d4-a716-446655440000
```

## UI方針

- 内部整数IDは原則非表示。
- UUIDも通常画面では非表示。
- 詳細確認・問い合わせ対応・ログ確認時のみ「内部識別子」として表示できる。
- 入力欄としてのID/コードは撤去する。
- 検索は名前・タイトル名・サブタイトル名を中心にする。

## Export / Import 方針

### Export

- CSV/JSONには `public_id` を含める。
- 既存互換のため当面は整数IDも含めてもよいが、画面説明では内部項目として扱う。

### Import

- 新規取込では `public_id` を優先する。
- `public_id` がない旧形式データは、取込時に新規生成する。
- 非空DBへのmerge/upsertは別フェーズで設計する。

## 操作履歴方針

- `change_logs.entity_id` は当面整数IDを維持する。
- 将来的に `entity_public_id` を追加する。
- 画面ではデータ名・操作・操作者・実行日時を主表示にする。
- UUID/内部IDは詳細確認用にする。

## migration案

### 0003_public_ids.sql

- 各対象テーブルに `public_id` を追加。
- 既存行はアプリ側 migration script で埋める。
- `public_id` に unique index を作る。

### migration script

SQLite単体SQLだけでUUID生成を完結させず、Python scriptで以下を行う。

1. DBを開く。
2. 対象テーブルを走査する。
3. `public_id IS NULL` の行に UUID を設定する。
4. unique index 作成済み/未作成を確認する。
5. 完了後に `PRAGMA integrity_check` 相当の確認を行う。

## 実装順

1. docsで移行方針を固定する。
2. domain/application層に UUID 生成 helper を追加する。
3. schema/migrationを追加する。
4. core serviceのcreate系で `public_id` を保存する。
5. query/read modelに `public_id` を追加する。
6. export/importに `public_id` を追加する。
7. UIから整数ID/コード露出をさらに削る。
8. 操作履歴に `entity_public_id` を追加する。

## リスクと対策

| リスク | 対策 |
|---|---|
| 既存テストが整数ID前提 | 整数IDは内部互換として維持 |
| 既存CSV/JSONとの互換性低下 | `public_id` なしの場合は取込時生成 |
| migration失敗 | 事前バックアップとdry-run scriptを用意 |
| UI上の識別が難しくなる | 名前・タイトル名・サブタイトル名を一意化して検索性を確保 |

## この設計PRでやらないこと

- 実スキーマ変更。
- 既存DB migration 実行。
- UIから全ID欄を完全撤去。
- export/import形式変更。

## 次PR候補

- `public_id` 追加 migration と UUID helper。
- create系 service で public_id 自動生成。
- export/importへの public_id 追加。

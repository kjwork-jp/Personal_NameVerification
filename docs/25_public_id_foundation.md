# public_id / UUID土台

## 目的

内部主キーである整数 `id` を維持しながら、将来的なUI表示・export/import・外部連携で使える安定IDとして `public_id` を追加する。

## 今回の範囲

- `names`
- `titles`
- `subtitles`
- `name_subtitle_links`
- `name_title_links`
- `change_logs`

上記テーブルに nullable な `public_id` 列を追加する。

## 互換性方針

既存DBを壊さないため、`public_id` は `NOT NULL` にしない。
既存行はアプリ起動時の `ensure_public_ids()` でバックフィルする。
新規行はSQLite triggerで `public_id` を補完する。

## 注意

今回のPRはDB土台のみであり、UI表示・read model・export/importでの `public_id` 利用は次段階とする。

## 次段階

1. read modelへ `public_id` を追加する。
2. export/importで `public_id` を保持する。
3. UI上の内部ID表示を `public_id` に寄せる。
4. 最終的に必要なら `public_id` の `NOT NULL` 化を検討する。

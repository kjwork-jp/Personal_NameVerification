# public_id / UUID土台

## 目的

内部主キーである整数 `id` を維持しながら、将来的なUI表示・export/import・外部連携で使える安定IDとして `public_id` を追加する。

## DB土台の範囲

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

## read model反映

`public_id` は以下のread modelへ任意フィールドとして追加する。

- `NameSearchRow`
- `NameDetail`
- `TitleDetail`
- `SubtitleDetail`
- `RelatedRow`
- `NameTitleLinkRow`
- `ChangeLogRow`

既存UI互換を優先し、整数 `id` は引き続き保持する。
`public_id` は外部連携・export/import・将来的なUI表示用として段階的に使う。

## public_id参照

`PublicIdQueryService` を追加し、外部向け `public_id` から現在DB内の整数IDへ解決できるようにする。

対象テーブル:

- `names`
- `titles`
- `subtitles`
- `name_subtitle_links`
- `name_title_links`
- `change_logs`

このserviceは外部連携や将来のimport差分解決で使うための土台であり、既存UI操作はまだ整数IDベースのままとする。

## 注意

今回の段階では、UI表示の `public_id` 置換はまだ完了していない。

## 次段階

1. UI上の内部ID表示を `public_id` に寄せる。
2. `public_id` で参照・検索できるqueryを追加する。
3. 最終的に必要なら `public_id` の `NOT NULL` 化を検討する。

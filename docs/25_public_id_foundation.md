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

## UI表示反映

名前管理画面の詳細欄に `公開ID` を併記する。
タイトル/サブタイトル管理画面では、タイトル選択ラベルとタイトル作成時の名前候補に短縮 `public_id` を併記する。

内部IDは既存処理互換のため保持し、操作対象は従来どおり内部IDで扱う。
テーブル上の内部ID列は引き続き非表示にする。

UI上のすべてのID表示を一括置換するのではなく、画面ごとに段階的に進める。

## 注意

今回の段階では、Link / Audit Log のUI表示置換はまだ完了していない。

## 次段階

1. export/importで `public_id` を保持する。
2. `public_id` で参照・検索できるqueryを追加する。
3. 関連付け・操作履歴の表示を段階的に `public_id` へ寄せる。
4. 最終的に必要なら `public_id` の `NOT NULL` 化を検討する。

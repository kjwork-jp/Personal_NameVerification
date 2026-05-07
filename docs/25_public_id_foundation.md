# public_id / UUID土台

## 目的

内部主キーである整数 `id` を維持しながら、将来的なUI表示・export/import・外部連携で使える安定IDとして `public_id` を追加する。

## DB土台

対象テーブル:

- `names`
- `titles`
- `subtitles`
- `name_subtitle_links`
- `name_title_links`
- `change_logs`

`public_id` は既存DB互換を優先し、現時点では nullable とする。
既存行はアプリ起動時に補完し、新規行はSQLite triggerで補完する。

## read model反映

以下のread modelに `public_id` 系フィールドを追加する。

- `NameSearchRow`
- `NameDetail`
- `TitleDetail`
- `SubtitleDetail`
- `RelatedRow`
- `NameTitleLinkRow`
- `ChangeLogRow`

## UI表示反映

公開IDの表示は段階的に進める。

- 名前管理: 詳細欄に公開IDを表示する。
- タイトル/サブタイトル管理: 選択中タイトルと名前候補に短縮公開IDを表示する。
- 関連付け: 名前、タイトル、サブタイトル、関連リンクに短縮公開IDを表示し、ツールチップに完全公開IDを出す。
- 操作履歴: 一覧と詳細ラベルに操作履歴の公開IDを表示する。

内部IDは既存処理互換のため保持し、操作対象は従来どおり内部IDで扱う。

## 次段階

1. 画面表示を確認する。
2. 必要に応じて列幅・表示文言を調整する。
3. 必要なら `public_id` の `NOT NULL` 化を検討する。

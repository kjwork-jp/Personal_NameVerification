# NameVerification 運用操作マニュアル（機能説明）

## 1. 導入（GitHub ZIP）
1. GitHub で `Code` → `Download ZIP` を選択する。
2. ZIP を展開し、作業フォルダを用意する。
3. 必要な依存を導入し、`python -m app.pyside6_main` で起動する。

## 2. 主要機能
- 名前管理（ID は自動採番。作成時に ID 手入力不要）
- タイトル/サブタイトル管理
- タイトル作成時の名前複数紐づけ
- 名前:タイトル 多対多（`name_title_links`）
- リンク管理（一覧選択ベース）
- 運用操作タブ（出力/取込/バックアップ/復元）
- ログビューア（source/status/action/filter/regex/ページング）

## 3. 名前↔タイトル紐づけ
- 1名前 → 複数タイトル
- 1タイトル → 複数名前
- 永続化テーブル: `name_title_links`

## 4. export/import
- CSV/JSON export/import 対象に `name_title_links` を含む。
- import は空DB限定。

## 5. RBAC 早見表
| 操作 | viewer | editor | admin |
|---|---|---|---|
| 名前↔タイトル link | × | ○ | ○ |
| 名前↔タイトル unlink | × | × | ○ |
| 名前↔タイトル restore/hard delete | × | × | ○ |
| export/backup | × | ○ | ○ |
| restore/import | × | × | ○ |

## 6. 障害時一次切り分け
- 起動不可: Python環境/依存/配布SHAを確認
- import失敗: 空DB条件・admin権限・ファイル形式確認
- ログ未表示: source/filter/ページ位置確認

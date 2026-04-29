# 運用マニュアル更新メモ

このブランチでは、運用開始前 blocker 修正に合わせて以下の運用ドキュメントを更新対象とします。

- `NameVerification_運用操作マニュアル_機能説明.xlsx`
- `NameVerification_運用手順書_詳細版.docx`
- `NameVerification_初回教育用_簡易マニュアル.docx`

## 反映済みの前提

- UI は日本語表示を前提にする。
- ID は DB 側で自動採番し、ユーザーに新規作成時の ID 入力をさせない。
- 名前とタイトルは `name_title_links` により直接多対多で紐づく。
- タイトル作成時に既存の名前を複数選択して紐づける。
- `name_title_links` は export/import 対象に含める。
- Operations ログビューアは filter / regex / sort / paging / 表示件数切替を前提にする。

## このチャット内で生成した成果物

GitHub コネクタのバイナリファイル直接アップロード制約により、xlsx/docx 本体はチャット添付成果物として生成済みです。リポジトリへ取り込む場合は、この README と同じ `docs/manuals/` 配下へ以下の3ファイルを追加してください。

1. `NameVerification_運用操作マニュアル_機能説明.xlsx`
2. `NameVerification_運用手順書_詳細版.docx`
3. `NameVerification_初回教育用_簡易マニュアル.docx`

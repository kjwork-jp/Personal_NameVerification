# NameVerification 初回教育用 簡易マニュアル

## 最初に覚える3点
- 画面表示は日本語。
- ID は自動採番（手入力しない）。
- 操作対象は一覧選択で指定する。

## まず実施する操作
1. GitHub ZIP を展開して起動。
2. 名前を新規作成。
3. タイトル作成時に名前を複数選択して紐づけ。
4. 紐づき表示を確認。
5. 運用操作タブで CSV 出力とログ確認。

## 重要ルール
- `name_title_links` が 名前↔タイトル 多対多を保持。
- `name_title_links` は export/import 対象。
- destructive 操作は admin のみ。

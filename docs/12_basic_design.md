# 12_basic_design.md

## 1. 目的
本書は、NameVerification v3 の機能構造・画面構造・層構造・起動構造を定義する。

## 2. 全体構成
- Presentation: PySide6 UI
- Application: UseCase / Service
- Domain: Entity / Value Object / Rule
- Infrastructure: SQLite, logging, file IO, backup/export/import

## 3. 起動点
- 正式起動点は `app/pyside6_main.py`
- UI は PySide6 に一本化
- 旧 UI を残さない

## 4. 画面構成
### 4.1 メインウィンドウ
- ヘッダー
- タブ
- ステータス領域

### 4.2 タブ
- 検索/照合
- マスタ管理
- ゴミ箱
- データ移行
- 監査/運用

## 5. 検索/照合タブ
- 検索バー
- 一致条件切替
- フィルタ
- 結果一覧
- 詳細表示

## 6. マスタ管理タブ
- 名前入力/更新
- タイトル入力/更新
- サブタイトル入力/更新
- リンク管理

## 7. ゴミ箱タブ
- 削除済み一覧
- 復元
- 完全削除

## 8. データ移行タブ
- Export
- Import
- Backup
- Restore

## 9. 監査/運用タブ
- 監査ログ一覧
- フィルタ
- レポート出力
- 運用ヘルプ

## 10. 層責務
### Presentation
- 入力受付
- 表示更新
- ダイアログ表示
- 状態通知

### Application
- ユースケース実行
- トランザクション制御
- 監査記録連携

### Domain
- 正規化
- 一意制約
- 状態遷移
- バリデーション

### Infrastructure
- DB 永続化
- ファイル出力
- バックアップ
- ログ保存

## 11. 主要設計原則
- 主導線は検索
- 入力系と参照系を分離
- destructive 操作は明示
- 運用導線をアプリ内から辿れる

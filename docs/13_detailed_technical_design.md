# 13_detailed_technical_design.md

## 1. 技術スタック
- Python 3.12
- PySide6
- SQLite3
- pytest
- pytest-cov
- ruff
- black
- mypy
- PyInstaller

## 2. 推奨ディレクトリ設計
```text
app/
  pyside6_main.py
  ui/
  application/
  domain/
  infrastructure/
db/
  schema.sql
  migrations/
scripts/
tests/
assets/
```

## 3. モジュール責務
### app/pyside6_main.py
正式エントリポイント。  
QApplication 初期化、MainWindow 起動、初期例外ハンドリングを担当。

### app/ui/
- MainWindow
- Tabs
- Dialogs
- Shared widgets

### app/application/
- Name use case
- Title use case
- Subtitle use case
- Link use case
- Import/export use case
- Backup/restore use case

### app/domain/
- Entities
- Value objects
- Validation rules
- Normalization rules
- State transition rules

### app/infrastructure/
- SQLite repository
- File repository
- Logger
- Backup handler
- Serializer

## 4. DB 方針
- SQLite を単一正本とする
- 論理削除は `deleted_at`
- 操作者は `operator_id`
- 監査は `change_logs`
- 一意性は DB 制約とアプリ制御の二重で担保

## 5. 例外方針
- ValidationError
- ConflictError
- PermissionError
- NotFoundError
- SystemError

## 6. ログ方針
- app log
- audit log
- backup/recovery log
- exception log

## 7. テスト方針
- domain: 単体
- application: 単体 + 結合
- UI: 最小限の統合
- scripts: CLI テスト
- UAT: 手順ベース

## 8. 配布方針
- PyInstaller により単一 exe 配布
- バージョンと SHA256 を記録
- 配布物は release ディレクトリへ格納

## 9. 実装禁止
- UI 層から SQL を直接叩く
- use case を飛ばして repository を呼ぶ
- 一時しのぎの命名を残す

# 51_backup_restore_policy.md

## 1. バックアップ方針
- 日次バックアップ
- 世代管理
- 実ファイル存在確認
- 復元可能性を定期確認
- restore/import のような destructive 操作では、実行前に現状DBを自動退避する

## 2. バックアップ対象
- SQLite DB
- 監査ログ
- 設定ファイル
- 必要に応じて assets

## 3. 復旧方針
- 破壊的復旧前に現状退避
- 復旧後に整合性確認
- 復旧記録を残す

## 4. 禁止
- 未確認バックアップを本番復旧に使う
- restore/import 前の退避DBパスを確認せずに destructive 操作を継続する

## 5. 実装ステータス（現時点）
- Day0/Day1 の実行順・初回チェック観点は `docs/58_operations_handoff_runbook_and_day1_checklist.md` を参照する。
- backup create（DB ファイルコピー）は実装済み。
- restore foundation（backup file から DB file 置換）は実装済み。
- backup 実行権限は editor/admin、viewer は不可。
- restore 実行権限は admin のみ（viewer/editor は不可）。
- restore 前に対象DBへのアクティブ接続をクローズする。
- restore 実行時は、復元前DBを `before_restore` として自動退避する。
- CSV / JSON import foundation（空DB限定）は実装済み。
- import 実行時は、取込前DBを `before_import` として自動退避する。
- SQL import は未実装（restore と責務分離）。
- UI では 運用操作 タブから最小導線を提供する。
- restore/import は destructive 扱いとして実行前確認ダイアログを必須とする。

## 6. 自動退避先
- portable配布で `30_prod_db/nameverification.db` を利用している場合:
  - restore前退避: `50_backups/before_restore/`
  - import前退避: `50_backups/before_import/`
- portable配布外のDBを利用している場合:
  - DBファイル隣接の `backups/before_restore/` または `backups/before_import/`

## 7. PR #117 後の確認観点
- invalid restore/import input では、退避DB作成より前に validation error で止まること。
- import service は `database_path` 未指定時も SQLite `PRAGMA database_list` から file-backed DB path を解決できること。
- UI / service / tests は restore/import の戻り値として退避DBパスを扱うこと。

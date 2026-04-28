# 51_backup_restore_policy.md

## 1. バックアップ方針
- 日次バックアップ
- 世代管理
- 実ファイル存在確認
- 復元可能性を定期確認

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


## 5. 実装ステータス（現時点）
- Day0/Day1 の実行順・初回チェック観点は `docs/58_operations_handoff_runbook_and_day1_checklist.md` を参照する。
- backup create（DB ファイルコピー）は実装済み。
- restore foundation（backup file から DB file 置換）は実装済み。
- backup 実行権限は editor/admin、viewer は不可。

- restore 実行権限は admin のみ（viewer/editor は不可）。
- restore 前に対象DBへのアクティブ接続をクローズする。

- CSV / JSON import foundation（空DB限定）は実装済み。
- SQL import は未実装（restore と責務分離）。

- UI では 運用操作 タブから最小導線を提供する。
- restore/import は destructive 扱いとして実行前確認ダイアログを必須とする。

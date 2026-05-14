# 50_operations_design.md

## 1. 目的
運用開始後に必要な日次・週次・障害時運用を定義する。

補助手順（Day0/Day1、初回チェック、一次切り分け）は `docs/58_operations_handoff_runbook_and_day1_checklist.md` を参照。

## 2. 日次運用
- 起動確認
- 運用操作 タブで日次運用操作（export/backup create）を実施
- path 指定は 運用操作 タブの 参照 ボタン（native dialog）を優先利用
- portable配布では初期表示を配布フォルダ配下（`50_backups/daily`,
  `60_exports/csv`, `60_exports/json`, `60_exports/sql`）に寄せる
- recent path history 候補を利用して再入力を省力化
- 運用操作 実行結果は JSONL（append-only）へ記録する
  - portable配布では `40_logs/operations_events.jsonl` を既定値とする
  - source/development 実行では従来どおり AppDataLocation 配下を既定値とする
  - `NAMEVERIFICATION_OPERATIONS_LOG_JSONL_PATH` が指定されている場合はその値を優先する
- 運用操作 実行は async worker で分離し、busy 中は二重起動を防止（cancel request 導線あり）
- 運用操作 ログは size-based rotation と TTL pruning でローカル保守を行う
- recent path history は 運用操作 タブから一括クリア可能
- 運用操作 タブのログビューで最新実行ログを再読込して確認する
- 必要に応じて archive 含有切替 / status-action filter / message 検索（部分一致・regex）で絞り込む
- regex 利用時は 大文字小文字を無視 / 複数行 / ドット改行一致 を必要に応じて切替する
- ログ表示順は 最新順 / 古い順 を切替して確認する
- ログ結果は 前へ/次へ ページングで確認し、選択 source（current/all/archive）補助表示を併用する
- ログ表示件数（50/100/200/500）を切替して確認観点に合わせる
- 代表検索確認
- 変更ログ確認
- 必要時の CSV / JSON / SQL dump 出力（editor/admin）
- 終業前バックアップ作成（editor/admin）

## 3. 週次運用
- 運用操作 タブ経由でバックアップ復元リハーサル（restore は admin 実行、事前に対象DB接続クローズ）
- restore 実行時は、アプリ側が復元前DBを `50_backups/before_restore/` 配下へ自動退避することを確認する
- import 実行時は、アプリ側が取込前DBを `50_backups/before_import/` 配下へ自動退避することを確認する
- portable配布外のDBでは、DBファイル隣接の `backups/before_restore/` または `backups/before_import/` が退避先になる
- 運用レポート確認
- change_logs spot review
- export / backup 出力ファイル妥当性サンプリング
- restore 実行前の接続クローズ確認
- 空DBへの初期 import（CSV/JSON, admin）手順確認
- 未処理課題確認

## 4. 月次運用
- バックアップ世代確認
- 権限設定棚卸し
- 障害 / 問い合わせ傾向レビュー

## 5. 運用ロール
- 運用担当
- 管理者
- 開発担当

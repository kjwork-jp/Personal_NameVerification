# 50_operations_design.md

## 1. 目的
運用開始後に必要な日次・週次・障害時運用を定義する。

## 2. 日次運用
- 起動確認
- Operations タブで日次運用操作（export/backup create）を実施
- path 指定は Operations タブの Browse ボタン（native dialog）を優先利用
- recent path history 候補を利用して再入力を省力化
- Operations 実行結果は AppDataLocation 配下の JSONL（append-only）へ記録
- Operations 実行は async worker で分離し、busy 中は二重起動を防止（cancel request 導線あり）
- 代表検索確認
- 変更ログ確認
- 必要時の CSV / JSON / SQL dump 出力（editor/admin）
- 終業前バックアップ作成（editor/admin）

## 3. 週次運用
- Operations タブ経由でバックアップ復元リハーサル（restore は admin 実行、事前に対象DB接続クローズ）
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

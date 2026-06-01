# Rich Admin UI v0.3 自動推進計画

## 方針

ユーザーは最終UAT中心とし、AI側で実装、PR作成、CI確認、必要なGitHub設定提案、マージ後同期手順提示まで進める。

## 対象

- SEARCH-TAB-RICHENING
- LIST-SUMMARY-COUNTERS
- TITLE-MGMT-SELECTION-REDESIGN
- LINK-LABEL-NORMALIZATION
- SUBTITLE-MGMT-SELECTION-REDESIGN
- DELETE-FLOW-CLARITY
- USER-MGMT-VISUAL-POLISH
- SHARED-RICH-UI-COMPONENTS
- AUDIT-DATAIO-HELP-POLISH

## 実行順

1. Phase 1: 検索タブのリッチ化と一覧件数可視化
2. Phase 2: タイトル管理・関連付けの対象選択UI刷新
3. Phase 3: 削除データ、ユーザー管理、監査ログ、Data I/O、Helpの視覚整備

## 守る制約

- DBスキーマ変更なし
- RBAC変更なし
- CRUDサービス変更なし
- public_id仕様変更なし
- 既存UAT互換を優先
- 起動コマンドは `python -m app.pyside6_main`

## 最終UAT観点

- 検索タブの視認性
- 件数・選択数の把握性
- 編集・削除対象の選択しやすさ
- 関連付けの名前/タイトル/サブタイトル/ID表記の分かりやすさ
- 全体のリッチ感

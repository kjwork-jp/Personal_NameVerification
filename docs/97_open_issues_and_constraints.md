# 97_open_issues_and_constraints.md

## 未解決事項
- UAT/Go-Live判定に使う「リリース基準SHA」の運用ルール（確定・変更時の再判定）
- 非空DBへの merge/overwrite/upsert import 方針
- SQL import を restore とどう分離して運用するか
- 実データ件数規模の最終見積
- アイコン保存方式の最終決定
- UAT 実施体制
- 配布先ディレクトリの最終決定
- read-only 権限のロール間差分（viewer/editor/admin）を将来どこまで分離するか
  - 候補: ゴミ箱/削除済み一覧、監査ログ、deleted 含む検索の閲覧範囲
  - 現時点は「valid role 共通 read-only 許可」を採用

## 制約
- Windows ローカル前提
- オフライン前提
- 単一拠点利用前提
- 現行実装は最小 RBAC（read-only は valid role 共通）であり、詳細差分は未実装

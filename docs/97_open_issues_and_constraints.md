# 97_open_issues_and_constraints.md

## 未解決事項
- 実データ件数規模の最終見積
- アイコン保存方式の最終決定
- read-only 権限のロール間差分（viewer/editor/admin）を将来どこまで分離するか
  - 候補: ゴミ箱/削除済み一覧、監査ログ、deleted 含む検索の閲覧範囲
  - 現時点は「valid role 共通 read-only 許可」を採用

## 解消済み・実装済み扱い
- v0.1.0-rc2 portable release のリリース証跡は `docs/59_release_evidence_v0_1_0_rc2.md` に固定済み
- UAT/Go-Live判定に使うリリース基準は v0.1.0-rc2 / PR #124 merge後の main として一旦固定済み
- UAT 実施体制と配布先ディレクトリ方針は `docs/63_distribution_and_uat_plan.md` にて決定済み
- PR #117 merge後のリリース資料・配布物メタ情報・checksum・manifest は v0.1.0-rc2 として再固定済み
- portable配布時のDB既定先は `30_prod_db/nameverification.db` に寄せる実装済み
- portable配布時のchange log JSONL既定先は `40_logs/change_logs.jsonl` に寄せる実装済み
- portable配布時のoperations log JSONL既定先は `40_logs/operations_events.jsonl` に寄せる実装済み
- restore/import 実行前のDB退避は実装済み
- invalid restore/import input は退避DB作成前に validation で止める方針へ整合済み
- import service は file-backed DB path の fallback 解決を実装済み
- SQLite DB 初期化時の親ディレクトリ作成保証は実装済み
- SQLite `PRAGMA integrity_check` は初期化時に実行済み
- portable release smoke script は実装済み
- 生成済み `release/` 成果物は Git 管理外にする方針へ整備済み
- 非空DBへの merge/overwrite/upsert import 方針は `docs/62_import_restore_policy_decision.md` にて、v0.1.0系では禁止継続として決定済み
- SQL import と restore の責務分離は `docs/62_import_restore_policy_decision.md` にて、SQL import未実装・DB全体復旧はrestore責務として決定済み

## 制約
- Windows ローカル前提
- オフライン前提
- 単一拠点利用前提
- 現行実装は最小 RBAC（read-only は valid role 共通）であり、詳細差分は未実装
- restore/import はadmin専用操作であり、実施前後のバックアップ証跡確認を運用で必須とする
- v0.1.0系ではCSV/JSON importは空DB限定とし、非空DBへのmerge/overwrite/upsert importは扱わない
- v0.1.0系ではSQL importは扱わず、DB全体復旧はrestoreで扱う

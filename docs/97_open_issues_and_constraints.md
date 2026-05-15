# 97_open_issues_and_constraints.md

## 未解決事項
- Day1業務CRUD/UAT本実施
  - 検索、CRUD、link、ゴミ箱、Audit、export、backup、権限、再起動後永続化の手動確認
  - 現時点のGo/No-Goは `docs/61_day0_day1_execution_record_v0_1_0_rc2_20260515.md` 上で Conditional Go
- 認証・ユーザー管理・管理設定の実装
  - 現行ログイン画面は認証ではなく、操作者IDとroleを利用者が任意選択できる
  - 複数ユーザー運用・第三者配布ではNo-Go
  - 詳細は `docs/66_security_user_management_gap_analysis.md` を参照
- DBファイル直アクセス対策・DB/backup/export/log保護
  - SQLite DBファイルを読めるOSユーザーはアプリを迂回して直接参照できる
  - 詳細は `docs/68_database_file_protection_policy.md` を参照
- 品質属性別の残存改善工程
  - 信頼性、可用性、保守性、完全性、機密性、ユーザビリティの不足機能を `docs/67_quality_attribute_gap_analysis.md` に洗い出し済み
  - P0は認証・ユーザー管理・role自由選択廃止・初回admin作成・ユーザー管理タブ

## 解消済み・実装済み扱い
- v0.1.0-rc2 portable release のリリース証跡は `docs/59_release_evidence_v0_1_0_rc2.md` に固定済み
- UAT/Go-Live判定に使うリリース基準は v0.1.0-rc2 / PR #124 merge後の main として一旦固定済み
- UAT 実施体制と配布先ディレクトリ方針は `docs/63_distribution_and_uat_plan.md` にて決定済み
- 実データ件数規模とアイコン保存方式は `docs/64_data_scale_and_asset_storage_policy.md` にて、v0.1.0系のGo/No-Go blockerではないと決定済み
- read-only 権限のロール間差分は `docs/65_readonly_rbac_future_policy.md` にて、v0.1.0系では valid role 共通許可、詳細分離は将来課題として決定済み
- 認証・ユーザー管理・管理設定の不足機能は `docs/66_security_user_management_gap_analysis.md` に洗い出し済み
- 品質属性別の残存改善工程は `docs/67_quality_attribute_gap_analysis.md` に洗い出し済み
- DBファイル直アクセスリスクと保護方針は `docs/68_database_file_protection_policy.md` に洗い出し済み
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
- 現行ログイン画面は認証ではなく、単一ユーザー・信頼済みローカル利用の暫定導線である
- 現行SQLite DB/backup/export/logは、OSユーザーが読める場所ではアプリを迂回して参照され得る
- restore/import はadmin専用操作であり、実施前後のバックアップ証跡確認を運用で必須とする
- v0.1.0系ではCSV/JSON importは空DB限定とし、非空DBへのmerge/overwrite/upsert importは扱わない
- v0.1.0系ではSQL importは扱わず、DB全体復旧はrestoreで扱う
- v0.1.0系ではアイコン・画像資産は実装対象外とし、将来扱う場合はassets配下の相対パス管理を第一候補とする
- v0.1.0系ではread-only操作はviewer/editor/adminのvalid role共通許可とし、詳細分離は将来課題とする
- 複数ユーザー運用・第三者配布・機微情報投入では、認証・ユーザー管理・管理設定・DB/backup/export/log保護の実装までNo-Goとする

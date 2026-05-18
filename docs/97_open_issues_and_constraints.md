# 97_open_issues_and_constraints.md

## 2026-05-18追記: v0.2.0 auth / RBAC / UI hardening 時点の補足

- 認証・ユーザー管理はPR #126〜#141相当の実装を経て、現在の `main` では初回admin setup、password login、DB role取得、user management、user audit log、RBAC UI hardeningまで進行済み。
- 現行ログイン画面は、旧来の「操作者IDとroleを利用者が任意選択する暫定導線」ではない。現在は `operator_id` + passwordでログインし、roleはDB上の `users.role` から取得する。
- MainWindowでは title bar / status bar に `ログイン中: <operator_id> / 権限: <role>` を常時表示する。
- viewerは完全参照専用へ寄せ、主要更新系UIは無効化済み。
- editorは通常登録/更新、関連付け登録、export/backupを許可し、destructive/import/restore/user管理/user audit log操作を禁止する方針。
- adminはdestructive/import/restore/user管理/user audit logを含む管理者権限。ただし最後の有効admin降格・無効化は禁止。
- 最新状況の横断台帳は `docs/75_v0_2_0_current_status_and_improvement_ledger.md` を参照する。

## 未解決事項

### P0: v0.2.0 UAT / release blocker

- 最新mainで品質ゲート再実行
  - `4f4c1d9`、`f926be4`、`6abc7e1`、`f0c4661` 以降で `pytest -q` / `ruff check .` / `black --check .` / `mypy app` を再実行する。
- editor role UAT本実施
  - 通常登録/更新、関連付け登録、export/backupが可能であることを確認する。
  - 削除、復元、完全削除、関連解除、import/restore、ユーザー管理、ユーザー監査ログ操作が不可であることを確認する。
- admin role UAT本実施
  - destructive/import/restore/user管理/user audit logを確認する。
  - 最後の有効admin降格・無効化が拒否されることを確認する。
- login異常系UAT
  - 誤password、未登録operator_id、disabled user、password confirmation不一致、空operator_id等を確認する。
- migration / 既存DB互換UAT
  - v0.1.0系DBからv0.2.0系へ起動時migrationできることを確認する。
- v0.2.0-rc1 portable package / smoke
  - release package生成、manifest/checksum、portable起動、portable smokeを確認する。

### P1: UI / usability改善

- データ入出力タブのサブタブ分割
  - ガイド / Export / Backup / Restore / Import / Operations Log へ分離する。
- 削除データタブの対象別分割
  - 削除済み名前 / 削除済みタイトル / 削除済みサブタイトル / 削除済みリンクへ分離する。
- 各タブへの操作ガイドサブタブ横展開
  - ユーザー管理では実装済み。名前、タイトル、サブタイトル、関連付け、削除データ、操作履歴、データ入出力、ヘルプ/設定へ展開する。
- 通常CRUD系画面の一覧起点化
  - 名前、タイトル、サブタイトル、関連付けを、一覧/登録/編集/操作/確認へ再構成する。
- RBAC UI自動テスト追加
  - viewer/editor/adminごとの主要button/input状態をテスト化する。

### P2: security / operations hardening

- DB/backup/export/log保護警告・診断
  - SQLite DBファイルを読めるOSユーザーはアプリを迂回して直接参照できる。
  - 詳細は `docs/68_database_file_protection_policy.md` を参照。
- ヘルプ/設定の診断画面化
  - ヘルプ / 設定 / パス診断 / 保護警告へ分割する。
- 監査ログのpassword非記録確認
  - screenshot範囲ではpassword平文は見えないが、JSON全体確認は未実施。

## 解消済み・実装済み扱い

- v0.1.0-rc2 portable release のリリース証跡は `docs/59_release_evidence_v0_1_0_rc2.md` に固定済み。
- UAT/Go-Live判定に使うリリース基準は v0.1.0-rc2 / PR #124 merge後の main として一旦固定済み。
- UAT 実施体制と配布先ディレクトリ方針は `docs/63_distribution_and_uat_plan.md` にて決定済み。
- 実データ件数規模とアイコン保存方式は `docs/64_data_scale_and_asset_storage_policy.md` にて、v0.1.0系のGo/No-Go blockerではないと決定済み。
- read-only 権限のロール間差分は `docs/65_readonly_rbac_future_policy.md` にて、v0.1.0系では valid role 共通許可、詳細分離は将来課題として決定済み。
- 認証・ユーザー管理・管理設定の不足機能は `docs/66_security_user_management_gap_analysis.md` に洗い出し済み。
- 品質属性別の残存改善工程は `docs/67_quality_attribute_gap_analysis.md` に洗い出し済み。
- DBファイル直アクセスリスクと保護方針は `docs/68_database_file_protection_policy.md` に洗い出し済み。
- v0.2.0設計の過不足は `docs/69_v0_2_0_design_completeness_review.md` に洗い出し済み。
- v0.2.0認証・ユーザー管理の実装計画は `docs/70_v0_2_0_auth_user_management_implementation_plan.md` に定義済み。
- v0.2.0統合UATチェックリストは `docs/71_v0_2_0_auth_integrated_uat_checklist.md` に定義済み。
- v0.2.0統合UAT実行記録は `docs/72_v0_2_0_auth_integrated_uat_execution_record.md` に記録中。
- UIナビゲーション再設計計画は `docs/73_ui_navigation_redesign_plan.md` に定義済み。
- RBAC強化計画は `docs/74_rbac_hardening_plan.md` に定義済み。
- v0.2.0現況/改善台帳は `docs/75_v0_2_0_current_status_and_improvement_ledger.md` に定義済み。
- 初回admin setup、password login、role自由選択廃止、DB role取得は実装済み。
- user management tab、user audit log tabは実装済み。
- MainWindow title/status barへのログイン中operator_id/role表示は実装済み。
- viewer向け主要RBAC UI hardeningは実装済み。
- editor向けデータ入出力制御はUI表示上確認済み。
- portable配布時のDB既定先は `30_prod_db/nameverification.db` に寄せる実装済み。
- portable配布時のchange log JSONL既定先は `40_logs/change_logs.jsonl` に寄せる実装済み。
- portable配布時のoperations log JSONL既定先は `40_logs/operations_events.jsonl` に寄せる実装済み。
- restore/import 実行前のDB退避は実装済み。
- invalid restore/import input は退避DB作成前に validation で止める方針へ整合済み。
- import service は file-backed DB path の fallback 解決を実装済み。
- SQLite DB 初期化時の親ディレクトリ作成保証は実装済み。
- SQLite `PRAGMA integrity_check` は初期化時に実行済み。
- portable release smoke script は実装済み。
- 生成済み `release/` 成果物は Git 管理外にする方針へ整備済み。
- 非空DBへの merge/overwrite/upsert import 方針は `docs/62_import_restore_policy_decision.md` にて、v0.1.0系では禁止継続として決定済み。
- SQL import と restore の責務分離は `docs/62_import_restore_policy_decision.md` にて、SQL import未実装・DB全体復旧はrestore責務として決定済み。

## 制約

- Windows ローカル前提。
- オフライン前提。
- 単一拠点利用前提。
- ローカルSQLite DB/backup/export/logは、OSユーザーが読める場所ではアプリを迂回して参照され得る。
- restore/import はadmin専用操作であり、実施前後のバックアップ証跡確認を運用で必須とする。
- v0.1.0系ではCSV/JSON importは空DB限定とし、非空DBへのmerge/overwrite/upsert importは扱わない。
- v0.1.0系ではSQL importは扱わず、DB全体復旧はrestoreで扱う。
- v0.1.0系ではアイコン・画像資産は実装対象外とし、将来扱う場合はassets配下の相対パス管理を第一候補とする。
- 複数ユーザー運用・第三者配布・機微情報投入では、アプリ内認証だけでなく、OS ACL / BitLocker / EFS / 配布先制限などの運用保護を併用する。

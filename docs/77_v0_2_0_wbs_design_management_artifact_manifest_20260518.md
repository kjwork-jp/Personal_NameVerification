# 77_v0_2_0_wbs_design_management_artifact_manifest_20260518.md

## 1. 目的

2026-05-18〜2026-05-19 時点の `v0.2.0 auth / RBAC / UI hardening / UAT` 作業について、WBS・設計書・管理台帳関連の更新対象と残件を整理する。

本資料は、外部提出用Excel台帳そのものではなく、GitHub上で追跡する **WBS/設計書/管理台帳の構成・更新方針・次工程マニフェスト** である。現況の正本は `docs/75_v0_2_0_current_status_and_improvement_ledger.md`、UAT実行記録は `docs/72_v0_2_0_auth_integrated_uat_execution_record.md`、未解決課題は `docs/97_open_issues_and_constraints.md` を参照する。

---

## 2. 直近の台帳更新対象

| No | 成果物 | 形式 | 更新頻度 | 役割 | 2026-05-19更新状態 |
|---:|---|---|---|---|---|
| 1 | `docs/72_v0_2_0_auth_integrated_uat_execution_record.md` | md | 都度更新 | UAT実行記録 | 更新済み |
| 2 | `docs/75_v0_2_0_current_status_and_improvement_ledger.md` | md | 都度更新 | 現況・改善台帳 | 更新済み |
| 3 | `docs/77_v0_2_0_wbs_design_management_artifact_manifest_20260518.md` | md | 都度更新 | WBS/設計書/管理台帳マニフェスト | 本更新で反映 |
| 4 | `docs/97_open_issues_and_constraints.md` | md | 都度更新 | 未解決事項・制約 | 更新済み |
| 5 | `app/pyside6_main.py` | py | 都度更新 | PySide6 entrypoint / account switch処理 | black整形反映済み |
| 6 | `scripts/smoke_test_portable_windows.ps1` | ps1 | リリース前 | portable package smoke | 実装済み、実行未完 |
| 7 | `Personal_NameVerification_WBS_工程管理台帳_vYYYYMMDD.xlsx` | xlsx | 都度更新 | 外部提出用WBS | 次回zip提出時に再生成対象 |
| 8 | `Personal_NameVerification_設計書_更新管理台帳_vYYYYMMDD.xlsx` | xlsx | 都度更新 | 外部提出用設計書更新管理 | 次回zip提出時に再生成対象 |
| 9 | `Personal_NameVerification_管理台帳_統合版_vYYYYMMDD.xlsx` | xlsx | 都度更新 | 外部提出用統合管理台帳 | 次回zip提出時に再生成対象 |

---

## 3. WBS成果物の構成

`Personal_NameVerification_WBS_工程管理台帳_vYYYYMMDD.xlsx`

| シート | 役割 | 更新観点 |
|---|---|---|
| `00_はじめに` | 版数、目的、正本、次回更新トリガー | 2026-05-19時点に更新 |
| `01_WBSサマリ` | WBS件数、完了/進行中/P0未完了、次工程 | ACC-WHITE-001、PORTABLE-001を反映 |
| `10_マイルストーン` | v0.1.0-rc2からv0.2.0-rc1までの節目 | UAT hardening完了、portable未完を反映 |
| `20_WBS_L1-L4` | 主要工程のL1-L4管理 | 認証/RBAC/UI/UAT/releaseを更新 |
| `21_WBS_L5詳細` | 品質ゲート、UAT、account switch、portableの実行単位 | `ACC-WHITE-001` を追加 |
| `30_工程進捗表` | 前後工程を含む進捗表 | 品質ゲートOK→再確認待ちに更新 |
| `40_UAT計画` | role別UAT計画 | login異常系/admin保護/data I/O/portableを残件化 |
| `50_UI改善WBS` | サブタブ化・ガイド横展開のWBS | 監査ログ統合、タイトル/サブタイトル統合は完了へ移動 |
| `60_RBAC_UAT_WBS` | RBAC確認計画 | viewer/editor/admin表示差分は概ね完了、実行系を残件化 |
| `90_入力規則リスト` | ステータス、優先度、担当、成果物種別、更新頻度 | 必要に応じて `後回し` を追加 |
| `99_最終レビュー` | 作成結果レビュー | 最新反映後に更新 |

---

## 4. 設計書更新管理台帳の構成

`Personal_NameVerification_設計書_更新管理台帳_vYYYYMMDD.xlsx`

| シート | 役割 | 更新観点 |
|---|---|---|
| `00_はじめに` | 目的、版数、正本 | 最新日付へ更新 |
| `10_設計書一覧` | README/docs/manualsの設計・運用・UAT資料一覧 | docs/72/75/77/97更新を反映 |
| `20_更新対象判定` | 都度更新/固定/参照のみ/old行きの判定 | docs/72/75/77/97は都度更新 |
| `30_設計変更台帳` | login context、RBAC、UIサブタブ化などの変更管理 | Windows認証、監査ログ統合、タイトル統合、account switch課題を追加 |
| `40_UI設計` | UI設計論点 | 権限なし操作非表示、関連付け表示改善を反映 |
| `50_RBAC設計` | viewer/editor/admin定義 | 最新RBAC表へ更新 |
| `60_運用設計` | 品質ゲート、証跡、配布方針 | portable smoke script追加、実行未完を反映 |
| `70_テスト設計` | viewer/editor/admin/migration/portableのテスト観点 | release remaining UAT / db initialization testsを反映 |
| `80_未反映_作成予定` | 将来反映候補 | ACC-WHITE-001の再設計、release evidenceを追加 |
| `99_最終レビュー` | 作成結果レビュー | 最新反映後に更新 |

---

## 5. 管理台帳統合版の構成

`Personal_NameVerification_管理台帳_統合版_vYYYYMMDD.xlsx`

| シート | 役割 | 更新観点 |
|---|---|---|
| `00_はじめに` | 目的、次回更新条件 | 最新commitと品質状況を反映 |
| `10_管理台帳総覧` | 各台帳と正本の対応 | docs/72/75/77/97を正本として明記 |
| `20_成果物管理` | GitHub資料/提出物の管理 | `02f65c4` / docs更新commitを追加 |
| `30_課題リスク管理` | 品質ゲート、UAT、account switch、portable | ACC-WHITE-001をP0残件として管理 |
| `40_変更管理` | UI/RBAC/docs変更の管理 | 監査ログ統合、タイトル統合、データ入出力RBAC、format修正 |
| `50_品質ゲート管理` | pytest/ruff/black/mypy/GUI起動確認 | 直近OK、docs更新後再確認待ち |
| `60_UAT実行管理` | role別UAT状況 | login異常系/admin保護/data I/O/portableを残件化 |
| `70_リリース管理` | v0.2.0-rc1 package/smoke/evidence | package/smoke/evidence未完 |
| `80_ロール権限管理` | viewer/editor/admin権限定義 | 最新RBAC表へ更新 |
| `90_次アクション` | 直近作業順 | 品質再確認→GUI終了確認→異常系/admin保護→portable |
| `99_最終レビュー` | 作成結果レビュー | 最新反映後に更新 |

---

## 6. 更新対象判定

| 区分 | 判定 | 理由 |
|---|---|---|
| 成果物一覧 | 都度更新 | 提出物と正本が増減するため |
| WBS/工程管理 | 都度更新 | 次工程・進捗・完了条件が変わるため |
| 設計書更新管理 | 都度更新 | 設計資料/未反映/変更履歴を管理するため |
| 管理台帳統合版 | 都度更新 | 課題、変更、品質、UAT、releaseが変化するため |
| UAT実行記録 | 都度更新 | 実行結果と証跡が増えるため |
| UI/RBAC設計資料 | 都度更新 | 改善事項と権限定義が変わるため |
| v0.1.0-rc2 release evidence | 固定 | 過去証跡のため直接更新しない |
| 旧チャットPDF | 参照のみ | 履歴資料。現況は台帳へ転記する |

---

## 7. 未実施事項

| 優先 | ID | 未実施事項 | 状態 |
|---:|---|---|---|
| P0 | GATE-001 | `02f65c4` / docs更新後の品質ゲート再実行 | 未実施 |
| P0 | GUI-001 | 最新main GUI通常起動・通常終了確認 | 未実施 |
| P0 | ACC-WHITE-001 | アカウント切替後の白画面/全ウィンドウ終了/プロセス残存の根治 | 後回し未解決 |
| P0 | AUTH-002 | login異常系UAT | 未実施 |
| P0 | ADMIN-001 | 最後の有効admin保護UAT | 未実施 |
| P0 | PORTABLE-001 | v0.2.0-rc1 portable package / smoke | 未実施 |
| P1 | DATAIO-002 | Export / Backup / Operations Log 実行UAT | 未実施 |
| P1 | RESTORE-001 | Restore / Import destructive操作UAT | 未実施 |
| P1 | AUDIT-002 | login_failure / role_change / disable / enable 監査ログUAT | 未実施 |
| P1 | RELEASE-001 | v0.2.0-rc1 release evidence作成 | 未実施 |

---

## 8. 次工程

1. 最新mainをpullする。
2. `black --check .` / `ruff check .` / `mypy app` / `pytest -q` を再実行する。
3. `python -m app.pyside6_main` で通常起動・通常終了を確認する。
4. `ACC-WHITE-001` は一旦後回し管理のまま残す。
5. login異常系UATを実施する。
6. 最後の有効admin保護UATを実施する。
7. editor/adminのExport/Backup/Restore/Import実行UATを実施する。
8. v0.2.0-rc1 package / portable smokeへ進む。
9. release evidenceを作成する。

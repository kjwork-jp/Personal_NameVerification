# 77_v0_2_0_wbs_design_management_artifact_manifest_20260518.md

## 1. 目的

2026-05-18 時点の `v0.2.0 auth / RBAC / UI hardening` 作業について、前回の成果物更新で不足していた **WBS・設計書・管理台帳関連** を追加で整理したことを記録する。

前回は `README` / `docs/72` / `docs/73` / `docs/74` / `docs/75` / `docs/76` / `docs/97` と、成果物一覧・引継ぎ・操作マニュアル中心の更新だった。今回の追加指摘を受け、工程管理・設計書管理・統合管理台帳まで含めて提出物を拡張する。

---

## 2. 今回追加した外部提出用成果物

| No | 成果物 | 形式 | 更新頻度 | 役割 |
|---:|---|---|---|---|
| 1 | `Personal_NameVerification_成果物一覧_更新管理台帳_v20260518_2.xlsx` | xlsx | 都度更新 | WBS/設計書/管理台帳まで含めた成果物一覧の最新版 |
| 2 | `Personal_NameVerification_WBS_工程管理台帳_v20260518.xlsx` | xlsx | 都度更新 | WBS L1-L4 / L5詳細 / 工程進捗 / UAT / UI改善 / RBAC UAT を管理 |
| 3 | `Personal_NameVerification_設計書_更新管理台帳_v20260518.xlsx` | xlsx | 都度更新 | 設計書一覧 / 更新対象判定 / 設計変更 / UI/RBAC/運用/テスト設計 / 未反映予定を管理 |
| 4 | `Personal_NameVerification_管理台帳_統合版_v20260518.xlsx` | xlsx | 都度更新 | 成果物、課題、変更、品質ゲート、UAT、リリース、ロール権限、次アクションを統合管理 |
| 5 | `Personal_NameVerification_追加更新_最終見直しレビュー_v20260518.txt` | txt | 都度更新 | 追加更新のレビュー結果 |
| 6 | `Personal_NameVerification_追加引継ぎメモ_v20260518_2.md` | md | 都度更新 | 今回追加分の引継ぎ補足 |
| 7 | `Personal_NameVerification_更新成果物一覧_v20260518_2.txt` | txt | 都度更新 | v20260518_2 提出物一覧 |
| 8 | `Personal_NameVerification_更新成果物一式_v20260518_2.zip` | zip | 都度更新 | 今回追加分と前回主要成果物を含む一式パッケージ |

---

## 3. WBS成果物の構成

`Personal_NameVerification_WBS_工程管理台帳_v20260518.xlsx`

| シート | 役割 |
|---|---|
| `00_はじめに` | 版数、目的、正本、次回更新トリガー |
| `01_WBSサマリ` | WBS件数、完了/進行中/P0未完了、次工程 |
| `10_マイルストーン` | v0.1.0-rc2からv0.2.0-rc1までの節目 |
| `20_WBS_L1-L4` | 主要工程のL1-L4管理 |
| `21_WBS_L5詳細` | 品質ゲート、editor/admin UAT、UI改善の実行単位 |
| `30_工程進捗表` | 前後工程を含む進捗表 |
| `40_UAT計画` | role別UAT計画 |
| `50_UI改善WBS` | サブタブ化・ガイド横展開のWBS |
| `60_RBAC_UAT_WBS` | RBAC確認計画 |
| `90_入力規則リスト` | ステータス、優先度、担当、成果物種別、更新頻度 |
| `99_最終レビュー` | 作成結果レビュー |

---

## 4. 設計書更新管理台帳の構成

`Personal_NameVerification_設計書_更新管理台帳_v20260518.xlsx`

| シート | 役割 |
|---|---|
| `00_はじめに` | 目的、版数、正本 |
| `10_設計書一覧` | README/docs/manualsの設計・運用・UAT資料一覧 |
| `20_更新対象判定` | 都度更新/固定/参照のみ/old行きの判定 |
| `30_設計変更台帳` | login context、RBAC、UIサブタブ化などの変更管理 |
| `40_UI設計` | UI設計論点 |
| `50_RBAC設計` | viewer/editor/admin定義 |
| `60_運用設計` | 品質ゲート、証跡、配布方針 |
| `70_テスト設計` | viewer/editor/admin/migration/portableのテスト観点 |
| `80_未反映_作成予定` | docs/58/70/71/manuals等の将来反映候補 |
| `99_最終レビュー` | 作成結果レビュー |

---

## 5. 管理台帳統合版の構成

`Personal_NameVerification_管理台帳_統合版_v20260518.xlsx`

| シート | 役割 |
|---|---|
| `00_はじめに` | 目的、次回更新条件 |
| `10_管理台帳総覧` | 各台帳と正本の対応 |
| `20_成果物管理` | GitHub資料/提出物の管理 |
| `30_課題リスク管理` | 品質ゲート未完、editor/admin UAT未完など |
| `40_変更管理` | UI/RBAC/docs変更の管理 |
| `50_品質ゲート管理` | pytest/ruff/black/mypy/GUI起動確認 |
| `60_UAT実行管理` | role別UAT状況 |
| `70_リリース管理` | v0.2.0-rc1 package/smoke/evidence |
| `80_ロール権限管理` | viewer/editor/admin権限定義 |
| `90_次アクション` | 直近作業順 |
| `99_最終レビュー` | 作成結果レビュー |

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

- 最新mainでの `pytest -q` / `ruff check .` / `black --check .` / `mypy app` 再実行。
- editor role 実行UAT。
- admin role 実行UAT。
- login異常系UAT。
- 最後の有効admin保護確認。
- 既存DB migration確認。
- v0.2.0-rc1 package / portable smoke。
- データ入出力/削除データ/通常CRUD系のサブタブ分割。

---

## 8. 次工程

1. 最新mainをpullする。
2. 品質ゲートを再実行する。
3. editor role UATを実施する。
4. admin role UATを実施する。
5. UAT結果を `docs/72` とExcel台帳へ反映する。
6. データ入出力タブを `ガイド / Export / Backup / Restore / Import / Operations Log` へ分割する。
7. 削除データタブを対象別に分割する。
8. v0.2.0-rc1 package / portable smokeへ進む。

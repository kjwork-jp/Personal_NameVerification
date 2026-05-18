# 76_v0_2_0_artifact_package_manifest_20260518.md

## 1. 目的

2026-05-18 時点の `v0.2.0 auth / RBAC / UI hardening` 作業について、Markdown資料だけでなく、Excel系・台帳系・レビュー系の成果物をまとめて更新したことを記録する。

今回のユーザー指摘は「成果物一覧から都度更新以上の資料は、Excel系も含めてまとめて更新すること」である。このため、`README` / `docs/72` / `docs/73` / `docs/74` / `docs/75` / `docs/97` に加え、外部提出用Excel/txt/md/zip成果物を生成した。

---

## 2. GitHub側で更新済みの資料

| commit | 対象 | 内容 |
|---|---|---|
| `f337920` | `README.md` | v0.2.0 RBAC / UI status / 参照資料を反映 |
| `bc247ab` | `docs/72_v0_2_0_auth_integrated_uat_execution_record.md` | editor確認・ログイン状態表示・残課題を反映 |
| `f0c4661` | `docs/74_rbac_hardening_plan.md` | RBAC定義・login context・editor状態を反映 |
| `6abc7e1` | `docs/73_ui_navigation_redesign_plan.md` | UI再設計計画にlogin context / backlogを反映 |
| `f926be4` | `docs/75_v0_2_0_current_status_and_improvement_ledger.md` | v0.2.0現況/改善台帳を新規追加 |
| 既更新 | `docs/97_open_issues_and_constraints.md` | v0.2.0 auth/RBAC/UI hardening時点へ整理済み |

---

## 3. 外部提出用に作成した成果物

| No | 成果物 | 形式 | 更新頻度 | 役割 |
|---:|---|---|---|---|
| 1 | `Personal_NameVerification_成果物一覧_更新管理台帳_v20260518.xlsx` | xlsx | 都度更新 | 成果物一覧を起点に、都度更新以上の対象・更新内容・残課題を管理 |
| 2 | `Personal_NameVerification_引継ぎマスター_v20260518.xlsx` | xlsx | 都度更新 | 現況、時系列、正本、実装状態、UAT、RBAC、次アクションを集約 |
| 3 | `NameVerification_運用操作マニュアル_機能説明_v2.0_20260518.xlsx` | xlsx | 都度更新 | v0.2.0 auth/RBAC対応の操作マニュアル・機能説明 |
| 4 | `Personal_NameVerification_最終見直しレビュー_v20260518.txt` | txt | 都度更新 | 今回の反映範囲、残課題、未実施事項の提出前レビュー |
| 5 | `Personal_NameVerification_新規チャット初回プロンプト_v20260518.md` | md | 都度更新 | 新規チャット引継ぎ用プロンプト |
| 6 | `Personal_NameVerification_更新成果物一覧_v20260518.txt` | txt | 都度更新 | 提出ファイル一覧 |
| 7 | `Personal_NameVerification_更新成果物一式_v20260518.zip` | zip | 都度更新 | 上記成果物の一式パッケージ |

---

## 4. 更新対象判定

今回の「都度更新以上」の判定対象は以下である。

| 区分 | 判定 |
|---|---|
| README / 総合案内 | 対象 |
| UAT実行記録 | 対象 |
| UI再設計計画 | 対象 |
| RBAC強化台帳 | 対象 |
| v0.2.0現況/改善台帳 | 対象 |
| 未解決課題/制約 | 対象 |
| 成果物一覧/更新管理台帳 | 対象 |
| 引継ぎマスター | 対象 |
| 運用操作マニュアル/機能説明 | 対象 |
| 最終見直しレビュー | 対象 |
| 新規チャット初回プロンプト | 対象 |
| v0.1.0-rc2 release evidence | 参照のみ。v0.2.0作業中のため今回は直接更新なし |
| docs/70 実装計画 | 要確認。PR分割・実装範囲変更時に更新 |
| docs/71 UATチェックリスト | 要確認。チェック項目追加時に更新 |
| docs/58 運用runbook | 次回候補。v0.2.0 RBACをさらに反映する余地あり |

---

## 5. 未実施事項

- 最新mainでの `pytest -q` / `ruff check .` / `black --check .` / `mypy app` 再実行。
- editor role 実行UAT。
- admin role 実行UAT。
- login異常系、最後の有効admin保護、既存DB migration、portable package smoke。
- データ入出力/削除データ/通常CRUD系のサブタブ横展開。

---

## 6. 次工程

1. 最新mainをpullする。
2. 品質ゲートを再実行する。
3. editor role UATを実施する。
4. admin role UATを実施する。
5. データ入出力タブを `ガイド / Export / Backup / Restore / Import / Operations Log` に分割する。
6. 削除データタブを対象別に分割する。
7. v0.2.0-rc1 package / portable smokeへ進む。

# 63_distribution_and_uat_plan.md

## 1. 目的

本書は、NameVerification v3 `v0.1.0-rc2` portable release の配布先、外部成果物の保管ルール、UAT実施体制を定義する。

対象:

- `v0.1.0-rc2`
- v0.1.0 系の後続パッチ

---

## 2. 結論

| 論点 | 決定 |
|---|---|
| 配布形態 | Windows portable ZIP |
| Git管理 | generated `release/`, `dist/`, `build/` はGit管理外 |
| 正本証跡 | `docs/59_release_evidence_v0_1_0_rc2.md` |
| Day0/Day1記録 | `docs/61_day0_day1_execution_record_v0_1_0_rc2_20260515.md` |
| 外部配布物 | ZIP / manifest / checksums / release evidence doc |
| UAT責任者 | owner: nkaji |
| Go判定 | Day1業務CRUD/UATの保留項目解消後にGoへ更新 |

---

## 3. 外部保管対象

| ID | 対象 | パス | 用途 |
|---|---|---|---|
| D-001 | portable ZIP | `release/NameVerification-v0.1.0-rc2-portable.zip` | 利用者へ渡す本体 |
| D-002 | manifest | `release/v0.1.0-rc2/00_manifest_v0.1.0-rc2_20260515.csv` | 配布物一覧・サイズ・hash確認 |
| D-003 | checksums | `release/v0.1.0-rc2/70_release_evidence/checksums_sha256_v0.1.0-rc2_20260515.txt` | ファイル単位のSHA256確認 |
| D-004 | release evidence | `docs/59_release_evidence_v0_1_0_rc2.md` | リリース固定情報の正本 |
| D-005 | Day0/Day1 record | `docs/61_day0_day1_execution_record_v0_1_0_rc2_20260515.md` | 実施結果・Go判定記録 |

---

## 4. 推奨ディレクトリ構成

Google Drive等の外部ストレージへ置く場合は、以下のように release 単位で分離する。

```text
52_名前解決アプリ/
└─ 30_release/
   └─ v0.1.0-rc2_20260515/
      ├─ NameVerification-v0.1.0-rc2-portable.zip
      ├─ 00_manifest_v0.1.0-rc2_20260515.csv
      ├─ checksums_sha256_v0.1.0-rc2_20260515.txt
      ├─ 59_release_evidence_v0_1_0_rc2.md
      └─ 61_day0_day1_execution_record_v0_1_0_rc2_20260515.md
```

このチャットではGoogleドライブを参照しないため、上記は外部配置時の推奨構成として扱う。

---

## 5. 配布前チェック

| ID | 確認項目 | コマンド/観点 | 期待値 |
|---|---|---|---|
| P-001 | Git状態 | `git status --short --branch` | `## main...origin/main` |
| P-002 | 生成物混入 | `git ls-files release dist build` | 出力なし |
| P-003 | ZIP hash | `Get-FileHash -Algorithm SHA256` | release evidenceと一致 |
| P-004 | manifest存在 | `Test-Path` | `True` |
| P-005 | checksums存在 | `Test-Path` | `True` |
| P-006 | portable smoke | `smoke_test_portable_release_windows.ps1` | success |
| P-007 | 文字化けfilename | mojibake/Japanese support filename grep | 出力なし |

---

## 6. UAT実施体制

| Role | 担当 | 責務 |
|---|---|---|
| Owner | nkaji | 実施判断、Go/No-Go判定、残課題起票 |
| Executor | nkaji | Day1手動UAT、証跡取得、記録更新 |
| Reviewer | ChatGPT / manual review | 記録・証跡・残課題の整合レビュー |

v0.1.0-rc2 は個人利用・ローカル運用前提のため、UAT体制は owner/executor を同一人物として扱う。

---

## 7. UAT範囲

| 区分 | 確認項目 | 必須 |
|---|---|---|
| 起動 | portable EXE直起動 | 必須 |
| DB | `30_prod_db/nameverification.db` 作成 | 必須 |
| 検索 | 完全一致/部分一致/絞込 | 必須 |
| CRUD | 名前/タイトル/サブタイトル作成・更新 | 必須 |
| Link | 名前↔タイトル / 名前↔サブタイトル | 必須 |
| Trash | 論理削除・復元・完全削除 | 必須 |
| Audit | CRUD/backup/exportの記録 | 必須 |
| Operations | CSV/JSON/SQL export、backup create | 必須 |
| Persistence | 再起動後データ永続化 | 必須 |
| Role | viewer/editor/admin 操作可否 | 必須 |
| Destructive | restore/import確認ダイアログ、自動退避 | 条件付き必須 |

---

## 8. Go / No-Go ルール

| 判定 | 条件 |
|---|---|
| Go | Day1必須項目がOK、blockerなし、配布物SHA一致、生成物Git混入なし |
| Conditional Go | Day0と配布物はOKだが、Day1一部項目が保留。実運用開始前に解消が必要 |
| No-Go | 起動不可、DB作成不可、主要CRUD不可、backup不可、配布物SHA不一致、生成物混入などのblockerあり |

---

## 9. 記録更新ルール

- UAT結果は `docs/61_day0_day1_execution_record_v0_1_0_rc2_20260515.md` に記録する。
- NG/保留は残課題表へ必ず起票する。
- blockerが出た場合はGo判定をNo-Goへ変更する。
- 証跡パスは可能な限り相対パスで記録する。
- 追加修正が発生した場合は、release evidence のSHA256を再固定する。

---

## 10. 残課題

| ID | 内容 | 方針 |
|---|---|---|
| DU-001 | 外部ストレージへの実配置 | Google Drive等の利用可能タイミングで実施 |
| DU-002 | Day1本実施 | 実運用開始前に実施 |
| DU-003 | UAT証跡のスクリーンショット化 | 必要に応じて追加 |

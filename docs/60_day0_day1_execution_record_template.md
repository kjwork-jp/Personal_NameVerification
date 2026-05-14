# 60_day0_day1_execution_record_template.md

## 1. 目的

本書は、NameVerification v3 の Day0 / Day1 実施結果を、あとから監査・再確認できる粒度で記録するためのテンプレートである。

- 対象: v0.1.0-rc2 以降の portable release
- 参照: `docs/58_operations_handoff_runbook_and_day1_checklist.md`
- リリース証跡: `docs/59_release_evidence_v0_1_0_rc2.md`

---

## 2. 実施メタ情報

| 項目 | 記録 |
|---|---|
| 実施区分 | Day0 / Day1 / 再実施 |
| 実施日 | YYYY-MM-DD |
| 実施者 |  |
| 端末名 |  |
| OS | Windows 11 など |
| 対象 release | v0.1.0-rc2 |
| 対象 Git SHA |  |
| ZIP path | `release/NameVerification-v0.1.0-rc2-portable.zip` |
| ZIP SHA256 |  |
| Manifest | `release/v0.1.0-rc2/00_manifest_v0.1.0-rc2_YYYYMMDD.csv` |
| Checksums | `release/v0.1.0-rc2/70_release_evidence/checksums_sha256_v0.1.0-rc2_YYYYMMDD.txt` |
| 総合判定 | OK / NG / 保留 |
| 備考 |  |

---

## 3. 事前確認

| ID | 確認項目 | 期待値 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| D0-001 | `git status --short --branch` | `## main...origin/main` |  |  |
| D0-002 | `git ls-files release dist build` | 出力なし |  |  |
| D0-003 | ZIP SHA256 | リリース証跡と一致 |  |  |
| D0-004 | manifest存在 | `True` |  |  |
| D0-005 | checksums存在 | `True` |  |  |
| D0-006 | 文字化け/日本語support filename検索 | 出力なし |  |  |
| D0-007 | portable smoke script | success |  |  |

---

## 4. Day0 チェック結果

| ID | 確認項目 | 期待値 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| D0-101 | EXE起動 | 異常終了なし |  |  |
| D0-102 | ログイン | viewer/editor/admin を選択可能 |  |  |
| D0-103 | タブ表示 | 検索/名前/タイトル・サブタイトル/リンク/ゴミ箱/監査ログ/運用操作 |  |  |
| D0-104 | DB作成 | `30_prod_db/nameverification.db` |  |  |
| D0-105 | change log target | `40_logs/change_logs.jsonl` |  |  |
| D0-106 | operations log target | `40_logs/operations_events.jsonl` |  |  |
| D0-107 | daily backup directory | `50_backups/daily` |  |  |
| D0-108 | export directory | `60_exports/csv`, `60_exports/json`, `60_exports/sql` |  |  |

---

## 5. Day1 チェック結果

| ID | 確認項目 | 期待値 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| D1-001 | 検索 | 完全一致/部分一致/絞込が可能 |  |  |
| D1-002 | 名前作成 | 登録できる |  |  |
| D1-003 | 名前更新 | 更新できる |  |  |
| D1-004 | タイトル作成 | 登録できる |  |  |
| D1-005 | サブタイトル作成 | 登録できる |  |  |
| D1-006 | 名前↔タイトル link | 作成/参照できる |  |  |
| D1-007 | 名前↔サブタイトル link | 作成/参照できる |  |  |
| D1-008 | ゴミ箱 | 論理削除後に表示される |  |  |
| D1-009 | Audit | 主要操作が記録される |  |  |
| D1-010 | CSV export | `60_exports/csv` に出力 |  |  |
| D1-011 | JSON export | `60_exports/json` に出力 |  |  |
| D1-012 | SQL dump export | `60_exports/sql` に出力 |  |  |
| D1-013 | Backup create | `50_backups/daily` にDB copy作成 |  |  |
| D1-014 | Operations log viewer | 実行ログを確認できる |  |  |
| D1-015 | 再起動後データ永続化 | 登録データが残る |  |  |

---

## 6. 権限確認

| ID | Role | 確認項目 | 期待値 | 結果 | 証跡/メモ |
|---|---|---|---|---|---|
| R-001 | viewer | read-only操作 | 可能 |  |  |
| R-002 | viewer | write/destructive操作 | 不可 |  |  |
| R-003 | editor | write操作 | 可能 |  |  |
| R-004 | editor | restore/import/完全削除 | 不可 |  |  |
| R-005 | editor | export/backup create | 可能 |  |  |
| R-006 | admin | read/write/destructive操作 | 可能 |  |  |
| R-007 | admin | restore/import確認ダイアログ | 表示される |  |  |
| R-008 | admin | before_restore/before_import自動退避 | 作成される |  |  |

---

## 7. 取得証跡

| ID | 証跡 | パス/内容 | 備考 |
|---|---|---|---|
| E-001 | ZIP SHA256 |  |  |
| E-002 | manifest |  |  |
| E-003 | checksums |  |  |
| E-004 | package script log |  |  |
| E-005 | portable smoke log |  |  |
| E-006 | app startup operation log |  |  |
| E-007 | backup create operation log |  |  |
| E-008 | export files |  |  |
| E-009 | backup DB |  |  |

---

## 8. 残課題・判断事項

| ID | 種別 | 内容 | 影響 | 対応方針 | 担当 | 期限 | 状態 |
|---|---|---|---|---|---|---|---|
| I-001 | blocker / backlog / memo |  |  |  |  |  | 未着手 |

---

## 9. Go / No-Go 判定

| 判定項目 | 結果 | コメント |
|---|---|---|
| Day0完了 | OK / NG / 保留 |  |
| Day1完了 | OK / NG / 保留 |  |
| blockerなし | OK / NG / 保留 |  |
| 配布物SHA一致 | OK / NG / 保留 |  |
| 生成物Git混入なし | OK / NG / 保留 |  |
| 最終判定 | Go / No-Go / Conditional Go |  |

---

## 10. 記録ルール

- `結果` は `OK / NG / 保留 / 対象外` のいずれかで記録する。
- NG/保留は必ず `8. 残課題・判断事項` に起票する。
- destructive操作を行った場合は、退避DBパスを必ず証跡に残す。
- ZIP SHA256・manifest・checksums は、リリース証跡と一致することを確認する。
- 生成済み `release/`, `dist/`, `build/` はGit管理対象外であることを確認する。

# 61_day0_day1_execution_record_v0_1_0_rc2_20260515.md

## 1. 目的

本書は、NameVerification v3 `v0.1.0-rc2` portable release の Day0 / Day1 実施結果を記録する。

- テンプレート: `docs/60_day0_day1_execution_record_template.md`
- リリース証跡: `docs/59_release_evidence_v0_1_0_rc2.md`
- Day0/Day1手順: `docs/58_operations_handoff_runbook_and_day1_checklist.md`

---

## 2. 実施メタ情報

| 項目 | 記録 |
|---|---|
| 実施区分 | Day0 / Day1 事前検証 |
| 実施日 | 2026-05-15 |
| 実施者 | nkaji |
| 端末名 | Windows local development machine |
| OS | Windows 11 |
| 対象 release | v0.1.0-rc2 |
| 対象 Git SHA | 10678f445a8a99e8daf4eedcc1ef86e86fa8bf43（PR #124 merge後） |
| ZIP path | `release/NameVerification-v0.1.0-rc2-portable.zip` |
| ZIP SHA256 | `577237D37CBA0964DF1C5CE685DAABD7B4216813018A1E671FEE6041D1DE0CAE` |
| Manifest | `release/v0.1.0-rc2/00_manifest_v0.1.0-rc2_20260515.csv` |
| Checksums | `release/v0.1.0-rc2/70_release_evidence/checksums_sha256_v0.1.0-rc2_20260515.txt` |
| 総合判定 | Conditional Go |
| 備考 | 自動検証・portable直起動・配布物固定はOK。業務CRUD/UATの手動全量確認はDay1本実施で継続。 |

---

## 3. 事前確認

| ID | 確認項目 | 期待値 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| D0-001 | `git status --short --branch` | `## main...origin/main` | OK | main / origin/main clean |
| D0-002 | `git ls-files release dist build` | 出力なし | OK | 生成物のGit混入なし |
| D0-003 | ZIP SHA256 | リリース証跡と一致 | OK | `577237D37CBA0964DF1C5CE685DAABD7B4216813018A1E671FEE6041D1DE0CAE` |
| D0-004 | manifest存在 | `True` | OK | `00_manifest_v0.1.0-rc2_20260515.csv` |
| D0-005 | checksums存在 | `True` | OK | `checksums_sha256_v0.1.0-rc2_20260515.txt` |
| D0-006 | 文字化け/日本語support filename検索 | 出力なし | OK | ASCII-only support filename確認済み |
| D0-007 | portable smoke script | success | OK | `smoke_test_portable_release_windows.ps1` 実行成功 |

---

## 4. Day0 チェック結果

| ID | 確認項目 | 期待値 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| D0-101 | EXE起動 | 異常終了なし | OK | `release/v0.1.0-rc2/10_app/NameVerification.exe` 起動確認済み |
| D0-102 | ログイン | viewer/editor/admin を選択可能 | OK | portable直起動時に問題なしのユーザー確認あり |
| D0-103 | タブ表示 | 検索/名前/タイトル・サブタイトル/リンク/ゴミ箱/監査ログ/運用操作 | OK | portable直起動時に問題なしのユーザー確認あり |
| D0-104 | DB作成 | `30_prod_db/nameverification.db` | OK | portable smoke scriptで作成確認済み |
| D0-105 | change log target | `40_logs/change_logs.jsonl` | OK | portable smoke scriptのtarget表示確認済み |
| D0-106 | operations log target | `40_logs/operations_events.jsonl` | OK | portable smoke scriptのtarget表示確認済み |
| D0-107 | daily backup directory | `50_backups/daily` | OK | backup create実行済み。ただし最終release生成後のDay1本実施で再確認する |
| D0-108 | export directory | `60_exports/csv`, `60_exports/json`, `60_exports/sql` | 保留 | Day1本実施でCSV/JSON/SQL dump出力を確認する |

---

## 5. Day1 チェック結果

| ID | 確認項目 | 期待値 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| D1-001 | 検索 | 完全一致/部分一致/絞込が可能 | 保留 | Day1本実施で確認 |
| D1-002 | 名前作成 | 登録できる | 一部OK | 直起動後の簡易登録確認あり。Day1本実施で証跡化する |
| D1-003 | 名前更新 | 更新できる | 保留 | Day1本実施で確認 |
| D1-004 | タイトル作成 | 登録できる | 保留 | Day1本実施で確認 |
| D1-005 | サブタイトル作成 | 登録できる | 保留 | Day1本実施で確認 |
| D1-006 | 名前↔タイトル link | 作成/参照できる | 保留 | Day1本実施で確認 |
| D1-007 | 名前↔サブタイトル link | 作成/参照できる | 保留 | Day1本実施で確認 |
| D1-008 | ゴミ箱 | 論理削除後に表示される | 保留 | Day1本実施で確認 |
| D1-009 | Audit | 主要操作が記録される | 一部OK | app startup / backup create / change log target確認済み。CRUD操作別の記録はDay1本実施で確認 |
| D1-010 | CSV export | `60_exports/csv` に出力 | 保留 | Day1本実施で確認 |
| D1-011 | JSON export | `60_exports/json` に出力 | 保留 | Day1本実施で確認 |
| D1-012 | SQL dump export | `60_exports/sql` に出力 | 保留 | Day1本実施で確認 |
| D1-013 | Backup create | `50_backups/daily` にDB copy作成 | OK | backup create成功ログ確認済み |
| D1-014 | Operations log viewer | 実行ログを確認できる | 一部OK | operations_events.jsonl出力確認済み。UI viewer操作はDay1本実施で確認 |
| D1-015 | 再起動後データ永続化 | 登録データが残る | 保留 | Day1本実施で確認 |

---

## 6. 権限確認

| ID | Role | 確認項目 | 期待値 | 結果 | 証跡/メモ |
|---|---|---|---|---|---|
| R-001 | viewer | read-only操作 | 可能 | 保留 | Day1本実施で確認 |
| R-002 | viewer | write/destructive操作 | 不可 | 保留 | Day1本実施で確認 |
| R-003 | editor | write操作 | 可能 | 保留 | Day1本実施で確認 |
| R-004 | editor | restore/import/完全削除 | 不可 | 保留 | Day1本実施で確認 |
| R-005 | editor | export/backup create | 可能 | 保留 | Day1本実施で確認 |
| R-006 | admin | read/write/destructive操作 | 可能 | 一部OK | adminでbackup create確認済み。destructive操作はDay1本実施で確認 |
| R-007 | admin | restore/import確認ダイアログ | 表示される | 保留 | Day1本実施で確認 |
| R-008 | admin | before_restore/before_import自動退避 | 作成される | 保留 | destructive操作実施時のみ確認 |

---

## 7. 取得証跡

| ID | 証跡 | パス/内容 | 備考 |
|---|---|---|---|
| E-001 | ZIP SHA256 | `577237D37CBA0964DF1C5CE685DAABD7B4216813018A1E671FEE6041D1DE0CAE` | final evidence |
| E-002 | manifest | `release/v0.1.0-rc2/00_manifest_v0.1.0-rc2_20260515.csv` | exists=True |
| E-003 | checksums | `release/v0.1.0-rc2/70_release_evidence/checksums_sha256_v0.1.0-rc2_20260515.txt` | exists=True |
| E-004 | package script log | `package_release_windows.ps1 -ReleaseName v0.1.0-rc2` | success |
| E-005 | portable smoke log | `smoke_test_portable_release_windows.ps1 -ReleaseName v0.1.0-rc2` | success |
| E-006 | app startup operation log | `40_logs/operations_events.jsonl` | target確認済み |
| E-007 | backup create operation log | `40_logs/operations_events.jsonl` | backup create成功ログ確認済み |
| E-008 | export files |  | Day1本実施で記録 |
| E-009 | backup DB | `50_backups/daily` | backup create確認済み。最終release後に再取得推奨 |

---

## 8. 残課題・判断事項

| ID | 種別 | 内容 | 影響 | 対応方針 | 担当 | 期限 | 状態 |
|---|---|---|---|---|---|---|---|
| I-001 | backlog | Day1業務CRUD/UATの手動全量確認が未完了 | 実運用Go判定の最終根拠が不足 | Day1本実施で検索/CRUD/link/ゴミ箱/Audit/export/権限を確認 | nkaji | 実運用開始前 | 未着手 |
| I-002 | backlog | 非空DB import方針が未確定 | 将来の既存データ取込時に運用判断が必要 | merge/overwrite/upsert方針を別途設計 | TBD | 次スプリント | 未着手 |
| I-003 | backlog | SQL importとrestoreの責務分離が未確定 | import/restore運用の誤用リスク | SQL importを実装するか、restore専用に固定するか決定 | TBD | 次スプリント | 未着手 |

---

## 9. Go / No-Go 判定

| 判定項目 | 結果 | コメント |
|---|---|---|
| Day0完了 | OK | package生成、portable smoke、Git混入なし、主要パス確認済み |
| Day1完了 | 保留 | 業務CRUD/UATの手動全量確認が未完了 |
| blockerなし | OK | 現時点で配布物固定を妨げるblockerなし |
| 配布物SHA一致 | OK | `577237D37CBA0964DF1C5CE685DAABD7B4216813018A1E671FEE6041D1DE0CAE` |
| 生成物Git混入なし | OK | `git ls-files release dist build` 出力なし |
| 最終判定 | Conditional Go | Day1本実施でCRUD/UATを完了する条件付きGo |

---

## 10. 記録ルール

- `結果` は `OK / NG / 保留 / 対象外` のいずれかで記録する。
- NG/保留は必ず `8. 残課題・判断事項` に起票する。
- destructive操作を行った場合は、退避DBパスを必ず証跡に残す。
- ZIP SHA256・manifest・checksums は、リリース証跡と一致することを確認する。
- 生成済み `release/`, `dist/`, `build/` はGit管理対象外であることを確認する。

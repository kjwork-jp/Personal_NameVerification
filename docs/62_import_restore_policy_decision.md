# 62_import_restore_policy_decision.md

## 1. 目的

本書は、NameVerification v3 の import / restore 周りの責務分離と、非空DBへの import 方針を定義する。

対象 release:

- v0.1.0-rc2
- v0.1.0 系の後続パッチ

結論として、v0.1.0 系では **非空DBへの import は禁止継続** とし、**SQL import は実装しない**。DB全体の置換・復旧は restore の責務とする。

---

## 2. 現状仕様

| 項目 | 現状 |
|---|---|
| CSV import | 空DB限定 |
| JSON import | 空DB限定 |
| SQL import | 未実装 |
| restore | backup DB file から現行DB fileを置換 |
| import前退避 | 実装済み。`before_import` に自動退避 |
| restore前退避 | 実装済み。`before_restore` に自動退避 |
| destructive確認 | restore/importで確認ダイアログあり |

---

## 3. 用語定義

| 用語 | 定義 |
|---|---|
| import | CSV/JSONなどの論理データを、現在のDBへ取り込む操作 |
| restore | DBファイル全体をバックアップから置換する復旧操作 |
| 非空DB | names/titles/subtitles/link/change_logs などに既存データがあるDB |
| merge | 既存データを残したまま新規データを追加する方式 |
| overwrite | 一致データを上書きする方式 |
| upsert | 存在すれば更新、無ければ追加する方式 |
| dry-run | 実データを変更せず、取込差分・衝突・エラーだけを確認する方式 |

---

## 4. 方針決定

### 4.1 v0.1.0 系の方針

| 論点 | 決定 |
|---|---|
| 非空DBへの CSV import | 禁止継続 |
| 非空DBへの JSON import | 禁止継続 |
| SQL import | 実装しない |
| DB全体復旧 | restore の責務 |
| 既存DB統合 | v0.2.0以降の検討対象 |
| merge/overwrite/upsert | v0.1.0 系では採用しない |

理由:

- 非空DB import は重複解決・ID衝突・link整合性・change log扱いが複雑で、v0.1.0 系の安全性を下げる。
- SQL import と restore の境界が曖昧になると、運用者が「論理取込」と「DB全体置換」を混同する。
- 現在の実運用開始段階では、空DB初期投入・backup・restore の導線を安定させる方が優先度が高い。

---

## 5. 運用ルール

### 5.1 CSV / JSON import

- 空DB限定で実施する。
- admin のみ実施可能とする。
- 実行前に `before_import` へ自動退避されることを確認する。
- 非空DBでの import は validation error として止める。
- 既存DBへの追記・上書き・統合用途には使わない。

### 5.2 restore

- DB全体の復旧・巻き戻しに使う。
- admin のみ実施可能とする。
- 実行前にアプリ側DB接続をクローズする。
- 実行前に `before_restore` へ自動退避されることを確認する。
- restore後は起動確認・検索確認・backup作成を行う。

### 5.3 SQL dump export

- 監査・保全・外部確認用の出力として扱う。
- v0.1.0 系では SQL dump を import input として扱わない。
- SQL dump からの復旧が必要な場合は、別作業としてDB再構築手順を設計する。

---

## 6. 禁止事項

| 禁止事項 | 理由 |
|---|---|
| 非空DBへCSV/JSONを直接importする | 重複・上書き・link不整合リスクが高い |
| SQL dumpをimportとして扱う | restoreとの責務混同を招く |
| restoreをmerge用途で使う | DB全体置換であり、差分統合ではない |
| before_import / before_restore の退避確認なしでdestructive操作を継続する | 復旧不能リスクがある |

---

## 7. v0.2.0 以降の検討候補

| 候補 | 内容 | 優先度 |
|---|---|---:|
| dry-run import | 取込前に件数・衝突・差分を表示 | 高 |
| public_id based upsert | public_id をキーに更新/追加を判定 | 中 |
| conflict report export | 重複・衝突一覧をCSV/JSON出力 | 中 |
| import transaction preview | 反映予定SQL/操作内容の事前確認 | 中 |
| non-empty DB merge import | 既存DBへの追加取込 | 低〜中 |
| SQL restore helper | SQL dumpから別DBを再構築する補助手順 | 低 |

---

## 8. Go / No-Go 判断への影響

v0.1.0-rc2 の Go / No-Go 判断において、非空DB import と SQL import は **未実装blockerではない**。

理由:

- v0.1.0-rc2 の運用範囲では、import は空DB初期投入用途に限定する。
- DB全体の保全・復旧は backup / restore で担保する。
- 非空DB統合は将来拡張であり、初期実運用開始の必須要件ではない。

---

## 9. 残課題

| ID | 内容 | 方針 |
|---|---|---|
| IR-001 | dry-run importの設計 | v0.2.0以降で検討 |
| IR-002 | upsert key の確定 | public_idを軸に検討 |
| IR-003 | conflict resolution UI | 必要性をUAT後に判断 |
| IR-004 | SQL dumpからの復旧手順 | restoreとは別の運用手順として検討 |

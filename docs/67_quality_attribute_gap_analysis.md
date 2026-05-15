# 67_quality_attribute_gap_analysis.md

## 1. 目的

本書は、NameVerification v3 `v0.1.0-rc2` 時点の不足機能・改善工程を、以下の品質属性ごとに網羅的に洗い出す。

- 信頼性
- 可用性
- 保守性
- 完全性
- 機密性
- ユーザビリティ

対象は、現行アプリの実装・運用・配布・UAT・将来拡張を含む。

---

## 2. 結論

`v0.1.0-rc2` は、単一ユーザー・信頼済みローカル端末での限定利用であれば実運用候補になり得る。

一方で、複数ユーザー運用、第三者配布、機微情報投入、本格業務利用を前提にすると、以下のP0/P1改善が不足している。

| 品質属性 | 最重要不足 | 優先度 |
|---|---|---:|
| 機密性 | パスワード認証、ユーザー管理、role自由選択廃止 | P0 |
| 完全性 | 非空DB import禁止のUI明確化、restore/import前後の整合チェック強化 | P0〜P1 |
| 信頼性 | 自動回帰UAT、DB破損時の復旧導線、異常終了時の安全処理 | P1 |
| 可用性 | 自動バックアップ世代管理、起動失敗時の復旧案内、ロック検知 | P1 |
| 保守性 | migration管理、設定管理、リリース/バックログ台帳の継続更新 | P1 |
| ユーザビリティ | 初回セットアップ、ユーザー管理タブ、操作ガイド、エラー文言改善 | P0〜P1 |

---

## 3. 評価前提

| 項目 | 前提 |
|---|---|
| 配布形態 | Windows portable ZIP |
| DB | SQLite local file |
| 運用 | ローカル・オフライン・単一拠点 |
| 現行ログイン | 認証ではなく、操作者IDとrole選択 |
| 現行RBAC | read-onlyはvalid role共通、writeはeditor/admin、destructiveはadmin |
| 現行import | CSV/JSONは空DB限定、SQL importなし |
| 現行restore | DBファイル全体置換 |

---

## 4. 信頼性ギャップ

信頼性 = 期待した処理が失敗しにくく、失敗時も壊れた状態を残しにくい性質。

| ID | 不足/リスク | 影響 | 優先度 | 対応案 |
|---|---|---|---:|---|
| REL-001 | Day1業務CRUD/UATが未完了 | 実運用品質の最終根拠が不足 | P0 | `docs/61` の保留項目を実施・更新 |
| REL-002 | UI操作の自動E2Eテスト不足 | 画面操作回帰を検知しづらい | P1 | pytest-qt等で代表操作を自動化 |
| REL-003 | 異常終了時のDB接続/transaction状態確認が弱い | 破損・中途半端な操作の検知遅れ | P1 | transaction境界・rollbackテスト追加 |
| REL-004 | DB破損時のユーザー向け復旧ガイド不足 | 起動失敗時に対応不能 | P1 | 起動時エラー画面、restore案内追加 |
| REL-005 | restore/import後の自動検証が限定的 | 復旧後の整合性確認漏れ | P1 | restore/import後にintegrity_check・件数サマリ表示 |
| REL-006 | backup/export結果の自動妥当性検証不足 | 出力できても壊れている可能性 | P1 | backup hash、export file existence/row count検証 |
| REL-007 | operation log書込失敗時がbest effortで見えづらい | 監査証跡欠落に気づきにくい | P2 | UI警告または診断画面に反映 |

---

## 5. 可用性ギャップ

可用性 = 必要なときに起動・利用・復旧できる性質。

| ID | 不足/リスク | 影響 | 優先度 | 対応案 |
|---|---|---|---:|---|
| AVL-001 | DBロック時の案内不足 | 複数起動/restore時に詰まる | P1 | 起動時・restore時にロック検知と案内 |
| AVL-002 | バックアップ世代管理UI不足 | 手動管理が増え、復旧点が不明瞭 | P1 | backup一覧、世代削除、最新backup表示 |
| AVL-003 | 自動バックアップスケジュールなし | 操作忘れで復旧点が不足 | P1 | 起動時/終了時/日次の自動backup設定 |
| AVL-004 | 起動失敗時のセーフモードなし | 設定/DB異常時に起動不能 | P2 | safe mode、DB選択、設定リセット導線 |
| AVL-005 | update/rollback手順が未整備 | 版上げ失敗時に戻しにくい | P2 | releaseごとのrollback手順追加 |
| AVL-006 | ZIP展開場所の権限チェック不足 | Program Files等で書込不可になり得る | P1 | 初回起動時に書込権限診断 |

---

## 6. 保守性ギャップ

保守性 = 変更・調査・修正・引継ぎがしやすい性質。

| ID | 不足/リスク | 影響 | 優先度 | 対応案 |
|---|---|---|---:|---|
| MNT-001 | DB migration管理が簡易schema適用中心 | 将来schema変更時に差分管理しづらい | P1 | migrations/導入、schema_version管理 |
| MNT-002 | 設定管理モデル未整備 | 管理設定タブを作りにくい | P1 | app_settings table/service追加 |
| MNT-003 | ユーザー管理系service未整備 | 認証/ユーザー管理の実装単位が未分離 | P0 | users service/repository追加 |
| MNT-004 | リリース台帳はdocs中心 | 長期運用で一覧性が落ちる | P2 | release index / backlog index作成 |
| MNT-005 | ログ/設定/DBの診断コマンド不足 | 障害調査に手作業が多い | P1 | diagnostic script追加 |
| MNT-006 | UIコンポーネントが肥大化するリスク | 画面追加で保守困難 | P2 | tab別presenter/view model分離を検討 |
| MNT-007 | v0.2.0 backlogの優先順位表不足 | 次工程の判断が曖昧 | P1 | backlog docをP0/P1/P2で整理 |

---

## 7. 完全性ギャップ

完全性 = データが欠落・重複・不整合・意図しない変更を起こしにくい性質。

| ID | 不足/リスク | 影響 | 優先度 | 対応案 |
|---|---|---|---:|---|
| INT-001 | 非空DB importは方針決定済みだがUI上の説明が不足し得る | 誤解してimportしようとする | P1 | import画面に「空DB限定」明示 |
| INT-002 | restore/import後の件数比較がない | 復旧/取込後の過不足検知が弱い | P1 | before/after件数サマリ表示 |
| INT-003 | exportのrow count/hash証跡不足 | export完全性の確認が弱い | P1 | export結果に件数・hashを表示/ログ記録 |
| INT-004 | public_id重複時の復旧導線不足 | 将来import/upsert時に問題化 | P2 | public_id診断・重複検出script |
| INT-005 | 削除/復元/完全削除の二重確認粒度 | 誤操作防止が不足し得る | P1 | destructive再認証、対象件数表示 |
| INT-006 | manual DB編集を検知できない | 外部編集による不整合を見逃す | P2 | 起動時schema/integrity/foreign_key_check診断 |
| INT-007 | foreign_key_check未実施 | FK不整合検知がintegrity_checkだけでは不足 | P1 | `PRAGMA foreign_key_check` を診断に追加 |

---

## 8. 機密性ギャップ

機密性 = 許可されていない人にデータ・操作権限を渡さない性質。

| ID | 不足/リスク | 影響 | 優先度 | 対応案 |
|---|---|---|---:|---|
| CONF-001 | password認証なし | 誰でもadmin選択可能 | P0 | operator_id + password認証 |
| CONF-002 | role自由選択 | 権限昇格を防げない | P0 | roleはuser recordから取得 |
| CONF-003 | ユーザー管理タブなし | 権限管理不能 | P0 | admin専用user management |
| CONF-004 | 初回admin作成導線なし | 安全な初期化不能 | P0 | first-run setup wizard |
| CONF-005 | password policyなし | 弱いpasswordを防げない | P1 | 最小長・複雑性・変更機能 |
| CONF-006 | lockoutなし | 総当たり耐性がない | P1 | failed_login_count/locked_until |
| CONF-007 | DB/backup暗号化なし | ファイルを取られると読める | P2 | 必要性判断。SQLCipher等は別検討 |
| CONF-008 | destructive再認証なし | 離席中操作・誤操作に弱い | P1 | password再入力dialog |
| CONF-009 | audit log閲覧分離なし | 監査内容が全roleで見える | P2 | v0.2以降で要否判断 |
| CONF-010 | secrets/設定保護なし | 将来外部連携時に漏えいリスク | P2 | secrets管理方針追加 |

---

## 9. ユーザビリティギャップ

ユーザビリティ = 迷わず、安全に、ミスしにくく操作できる性質。

| ID | 不足/リスク | 影響 | 優先度 | 対応案 |
|---|---|---|---:|---|
| UX-001 | ログイン画面が認証に見えるが実際はrole選択 | 誤認・危険 | P0 | 認証実装、または暫定警告文を強化 |
| UX-002 | 初回セットアップがない | 初回利用者が何をすべきか不明 | P0 | first-run wizard |
| UX-003 | ユーザー管理画面がない | 管理導線が存在しない | P0 | admin tab追加 |
| UX-004 | 空DB import限定の説明不足 | 操作エラーの理由が伝わりにくい | P1 | UI説明、preflight result表示 |
| UX-005 | backup/export/restoreの違いが直感的でない可能性 | 誤操作リスク | P1 | 操作説明、危険度ラベル、確認dialog改善 |
| UX-006 | エラーメッセージが技術寄りになる可能性 | 利用者が復旧できない | P1 | ユーザー向けエラー文言整備 |
| UX-007 | Day1/UATチェックをUIから実施できない | 証跡取得が手作業 | P2 | diagnostics/checklist tab |
| UX-008 | 操作後の結果サマリ不足 | 成功した内容が分かりにくい | P1 | 件数・出力先・hash・backup pathを明示 |
| UX-009 | role別で無効ボタン理由が不明 | なぜ押せないか分からない | P2 | tooltip/status message |
| UX-010 | help/about画面不足 | version/SHA/paths確認が手間 | P1 | About/Diagnostics dialog |

---

## 10. 管理・運用設定ギャップ

| ID | 不足/リスク | 影響 | 優先度 | 対応案 |
|---|---|---|---:|---|
| OPS-001 | 管理設定タブなし | policy変更がコード/環境依存 | P1 | app_settings + admin settings tab |
| OPS-002 | backup retention設定なし | 容量肥大化/世代不足 | P1 | 世代数/保持日数設定 |
| OPS-003 | log retention設定UIなし | ログ肥大化管理が手作業 | P2 | retention UI |
| OPS-004 | export/import既定パス管理UIなし | 運用標準化しにくい | P2 | path settings |
| OPS-005 | release/version表示なし | 問い合わせ時に版が不明 | P1 | About dialogにversion/SHA表示 |
| OPS-006 | 診断情報exportなし | 障害報告に必要情報が集まらない | P1 | diagnostic bundle出力 |
| OPS-007 | 操作手順ガイドがアプリ内にない | docsを見ないと分からない | P2 | help tab/README viewer |

---

## 11. 優先度別ロードマップ

### P0: 次リリースで最優先

| ID | 内容 |
|---|---|
| P0-001 | password認証実装 |
| P0-002 | role自由選択廃止 |
| P0-003 | 初回admin作成 |
| P0-004 | users table / user service |
| P0-005 | admin専用ユーザー管理タブ |
| P0-006 | 管理者最低1人保証 |
| P0-007 | ログイン画面の認証化または暫定警告強化 |

### P1: 実運用安定化

| ID | 内容 |
|---|---|
| P1-001 | login成功/失敗audit |
| P1-002 | password変更/リセット |
| P1-003 | lockout / failed login counter |
| P1-004 | destructive再認証 |
| P1-005 | backup/export/restore結果サマリ強化 |
| P1-006 | foreign_key_check診断 |
| P1-007 | About/Diagnostics dialog |
| P1-008 | 管理設定タブ |
| P1-009 | backup retention設定 |
| P1-010 | UAT自動化/E2E代表操作テスト |

### P2: 中期改善

| ID | 内容 |
|---|---|
| P2-001 | DB/backup暗号化要否判断 |
| P2-002 | read-only詳細分離 |
| P2-003 | assets管理 |
| P2-004 | dry-run import / upsert import |
| P2-005 | 件数別ベンチマーク |
| P2-006 | installer/署名 |
| P2-007 | 診断bundle出力 |

---

## 12. 結論

現行の `v0.1.0-rc2` は、配布物・DB配置・backup/export/restore基盤としてはかなり整っている。一方で、認証・ユーザー管理・管理設定・運用診断・完全性検証・UXガードの不足が大きい。

次工程は、単なるDay1/UATではなく、v0.2.0へ向けた **security/user management hardening** をP0として開始するのが妥当である。
